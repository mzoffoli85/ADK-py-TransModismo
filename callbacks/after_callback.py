from typing import Optional
from google.adk.agents.callback_context import CallbackContext
from google.genai import types

# Marcadores auténticos por estilo — cuántos aparecen determina el score
STYLE_MARKERS: dict[str, list[str]] = {
    "flaite": [
        "wn", "weón", "weona", "cuestión", "altiro", "al tiro",
        " po", "caleta", "fome", "cachar", "puta", "luca", "penca",
        "bacán", "la pega", "chela", "copete", "tení", "sabí", "podí",
    ],
    "cuico": [
        "brevedad", "estimado", "estimada", "aquello", "corresponde",
        "podrías", "hacerme llegar", "amable", "pertinente", "excelente",
        "en lo personal", "me parece", "coordinar", "instancia",
    ],
    "politico": [
        "marco de", "evaluaremos", "compromiso", "ciudadanía", "instancia",
        "transparencia", "gestión", "menester", "es menester", "pertinentes",
        "se evaluará", "se analizará", "se está trabajando", "diálogo",
    ],
    "abuela": [
        "mijito", "mijita", "mi niño", "mi niña", "cuando puedas",
        "no se te olvide", "dios", "ay", "mi alma", "con calma",
        "me da penita", "cuídate", "bendiga", "acompañe",
    ],
    "startup": [
        "asap", "handoff", "alinear", "roadmap", "feedback",
        "sprint", "delivery", "kpi", "sync", "meeting", "pivotear",
        "onboarding", "stack", "scope", "ownership",
    ],
}


def score_output(text: str, tipo: str) -> tuple[int, str]:
    """Evalúa autenticidad del estilo. Retorna (score 1-10, razón)."""
    markers = STYLE_MARKERS.get(tipo, [])
    text_lower = text.lower()

    matches = [m for m in markers if m in text_lower]
    count = len(matches)

    if count == 0:
        score, label = 2, "sin marcadores del estilo"
    elif count == 1:
        score, label = 5, "1 marcador"
    elif count == 2:
        score, label = 7, "2 marcadores"
    elif count == 3:
        score, label = 8, "3 marcadores"
    else:
        score = min(10, 8 + (count - 3))
        label = f"{count} marcadores"

    found = ", ".join(f'"{m}"' for m in matches[:5]) if matches else "ninguno"
    reason = f"{label} encontrados: {found}"
    return score, reason


def after_agent_callback_log(callback_context: CallbackContext) -> Optional[types.Content]:
    """ADK observability: registra cada intento y actualiza el contador."""
    attempts = callback_context.state.get("attempts", 0)
    tipo = callback_context.state.get("tipo", "?")

    print(
        f"  [after_callback] Respuesta recibida — intento {attempts + 1}, estilo '{tipo}'",
        flush=True,
    )

    # Incrementar para que before_callback sepa que ya hubo al menos un intento
    callback_context.state["attempts"] = attempts + 1
    return None
