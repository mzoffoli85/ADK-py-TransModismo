import argparse
import asyncio
import sys

from dotenv import load_dotenv
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types as genai_types

from agent import create_agent
from callbacks.before_callback import validate_input
from callbacks.after_callback import score_output

load_dotenv()

ESTILOS = ["flaite", "cuico", "politico", "abuela", "startup"]
MAX_ATTEMPTS = 3
MIN_SCORE = 7


async def run() -> None:
    parser = argparse.ArgumentParser(description="ADK PoC #4 — Modismo Translator")
    parser.add_argument("--tipo", required=True, choices=ESTILOS,
                        metavar="TIPO", help=f"Estilo: {', '.join(ESTILOS)}")
    parser.add_argument("--msg", required=True, help="Mensaje a transformar")
    args = parser.parse_args()

    tipo: str = args.tipo
    msg: str = args.msg

    # --- before_callback (standalone) -------------------------------------------
    # Valida antes de crear sesión. El before_agent_callback del agente también
    # interceptará la primera llamada al runner como guardrail adicional.
    error = validate_input(tipo, msg)
    if error:
        print(f"ERROR (before_callback): {error}", file=sys.stderr)
        sys.exit(1)

    # --- Setup ADK ---------------------------------------------------------------
    session_service = InMemorySessionService()
    session = await session_service.create_session(
        app_name="modismo",
        user_id="user",
        state={"tipo": tipo, "msg": msg, "attempts": 0},
    )

    agent = create_agent(tipo)
    runner = Runner(agent=agent, app_name="modismo", session_service=session_service)

    # --- Retry loop --------------------------------------------------------------
    best_result = ""
    best_score = 0
    total_attempts = 0

    for attempt in range(1, MAX_ATTEMPTS + 1):
        total_attempts = attempt

        if attempt == 1:
            user_msg = f'Transforma este mensaje al estilo {tipo}: "{msg}"'
        else:
            user_msg = (
                f'Intento {attempt}. Tu versión anterior obtuvo un score de {best_score}/10. '
                f'Necesita más marcadores auténticos del estilo {tipo}. '
                f'Transforma de nuevo: "{msg}"'
            )

        print(f"\n[Intento {attempt}/{MAX_ATTEMPTS}]", flush=True)

        # Ejecutar agente
        response_text = ""
        async for event in runner.run_async(
            user_id="user",
            session_id=session.id,
            new_message=genai_types.Content(
                role="user",
                parts=[genai_types.Part(text=user_msg)],
            ),
        ):
            if event.is_final_response() and event.content and event.content.parts:
                response_text = event.content.parts[0].text.strip()

        if not response_text:
            print("  Sin respuesta del agente.", flush=True)
            continue

        # --- after_callback (scoring) --------------------------------------------
        score, reason = score_output(response_text, tipo)
        print(f"  Score: {score}/10 — {reason}", flush=True)

        if score > best_score:
            best_score = score
            best_result = response_text

        if score >= MIN_SCORE:
            break

    # --- Output final ------------------------------------------------------------
    print()
    print(f"ORIGINAL  : {msg}")
    print(f"ESTILO    : {tipo}")
    print(f"RESULTADO : {best_result}")
    print(f"SCORE     : {best_score}/10")
    print(f"INTENTOS  : {total_attempts}")


if __name__ == "__main__":
    asyncio.run(run())
