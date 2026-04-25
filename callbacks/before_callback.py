from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

ESTILOS = ["flaite", "cuico", "politico", "abuela", "startup"]
MAX_MSG_LEN = 500


def validate_input(tipo: str, msg: str) -> Optional[str]:
    """Valida tipo y msg. Retorna mensaje de error o None si es válido."""
    if tipo not in ESTILOS:
        return f"tipo '{tipo}' no válido. Opciones permitidas: {', '.join(ESTILOS)}"
    if not msg or not msg.strip():
        return "El mensaje no puede estar vacío."
    if len(msg) > MAX_MSG_LEN:
        return f"El mensaje excede {MAX_MSG_LEN} caracteres ({len(msg)} recibidos)."
    return None


def before_agent_callback(callback_context: CallbackContext) -> Optional[types.Content]:
    """ADK guardrail: bloquea inputs inválidos antes de llegar al agente.

    Solo valida en el primer intento (attempts == 0).
    En reintentos, el input ya fue validado.
    """
    tipo = callback_context.state.get("tipo", "")
    msg = callback_context.state.get("msg", "")
    attempts = callback_context.state.get("attempts", 0)

    if attempts > 0:
        print(f"  [before_callback] Intento {attempts + 1} — validación omitida", flush=True)
        return None

    print(f"  [before_callback] Validando input: tipo='{tipo}', msg_len={len(msg)}", flush=True)
    error = validate_input(tipo, msg)

    if error:
        print(f"  [before_callback] BLOQUEADO: {error}", flush=True)
        return types.Content(
            role="model",
            parts=[types.Part(text=f"[before_callback bloqueó la ejecución]: {error}")],
        )

    print(f"  [before_callback] Input válido — pasando al agente", flush=True)
    return None
