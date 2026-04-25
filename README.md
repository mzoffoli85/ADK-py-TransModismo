# ADK PoC #4 — Modismo Translator

Transforma mensajes a estilos de habla chilena usando **Google ADK** con **Callbacks + Guardrails**.

## Estilos disponibles

| `--tipo`    | Descripción                              |
|-------------|------------------------------------------|
| `flaite`    | Jerga popular urbana chilena             |
| `cuico`     | Chileno clase alta, formal y afectado    |
| `politico`  | Lenguaje político evasivo                |
| `abuela`    | Abuelita chilena, cariñosa y con dichos  |
| `startup`   | Spanglish tech, todo en inglés y urgente |

## Instalación

```bash
pip install -r requirements.txt
cp .env.example .env
# editar .env con tu DEEPSEEK_API_KEY
```

## Uso

```bash
python main.py --tipo flaite   --msg "necesito que me envíes el documento hoy"
python main.py --tipo cuico    --msg "oye mándame eso"
python main.py --tipo politico --msg "no sé qué hacer con este problema"
python main.py --tipo abuela   --msg "llámame cuando puedas"
python main.py --tipo startup  --msg "hay que reunirse para ver el proyecto"
```

## Output esperado

```
[Intento 1/3]
  [before_callback] Validando input: tipo='flaite', msg_len=42
  [before_callback] Input válido — pasando al agente
  [after_callback] Respuesta recibida — intento 1, estilo 'flaite'
  Score: 8/10 — 3 marcadores: "wn", "cuestión", " po"

ORIGINAL  : necesito que me envíes el documento hoy
ESTILO    : flaite
RESULTADO : oye wn, pásame esa cuestión altiro po
SCORE     : 8/10
INTENTOS  : 1
```

## Conceptos ADK practicados

| Concepto | Implementación |
|---|---|
| **before_agent_callback** | Bloquea inputs inválidos antes de llegar al LLM |
| **after_agent_callback** | Registra cada intento (observabilidad) |
| **Guardrails** | Lista blanca de estilos + límite de longitud |
| **Retry con contexto** | El loop reintenta con feedback del score anterior |
| **Observabilidad** | Log de cada intento con score y marcadores encontrados |

## Variables de entorno

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
```

> Usa DeepSeek vía LiteLLM — API OpenAI-compatible apuntando a `deepseek/deepseek-chat`.
