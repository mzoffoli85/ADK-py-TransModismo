from pathlib import Path
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from callbacks.before_callback import before_agent_callback
from callbacks.after_callback import after_agent_callback_log

PROMPTS_DIR = Path(__file__).parent / "prompts"


def _load(path: Path) -> str:
    return path.read_text(encoding="utf-8").strip()


def create_agent(tipo: str) -> Agent:
    """Crea el ModismoAgent con callbacks y contexto del estilo cargado."""
    base_prompt = _load(PROMPTS_DIR / "transform_prompt.txt")
    style_guide = _load(PROMPTS_DIR / "estilos" / f"{tipo}.txt")

    instruction = (
        f"{base_prompt}\n\n"
        f"## ESTILO OBJETIVO: {tipo.upper()}\n\n"
        f"{style_guide}"
    )

    return Agent(
        name="modismo_agent",
        model=LiteLlm(model="deepseek/deepseek-chat"),
        instruction=instruction,
        before_agent_callback=before_agent_callback,
        after_agent_callback=after_agent_callback_log,
    )
