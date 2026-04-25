# ADK PoC #4 — Modismo Translator
> Este archivo es el inicializador del proyecto. Léelo completo antes de escribir una sola línea de código.

---

## Contexto del proyecto

Cuarto PoC de una serie de 5 construidos con **Google ADK** en Python. El foco de este PoC es **Callbacks y Guardrails** — capas de control que interceptan el comportamiento del agente antes y después de cada acción.

**Serie completa:**
1. ✅ Daily Brief *(Tool Use + Tool Chaining)*
2. ✅ Academic Researcher *(Multi-agent + Delegation)*
3. ✅ Knowledge Builder *(State + Memory + Sessions)*
4. 👉 **Modismo Translator** *(Callbacks + Guardrails)* ← este proyecto
5. ⬜ Live API Agent *(Streaming + Live API)*

---

## Objetivo del PoC

Dado un mensaje en texto plano y un estilo objetivo, el agente transforma el mensaje usando modismos locales chilenos. Los callbacks garantizan que el input sea válido y que el output sea auténtico al estilo solicitado.

---

## ¿Qué hace el sistema?

```
INPUT:
  --tipo  : tipo de transformación (flaite, cuico, político, abuela, startup)
  --msg   : mensaje en texto plano

FLUJO:
1. Before callback  → valida que --tipo sea un estilo permitido
                      y que --msg no esté vacío ni sea demasiado largo
2. El agente transforma el mensaje al estilo solicitado
3. After callback   → evalúa autenticidad del modismo en el output
                      (¿tiene rasgos reales del estilo o es genérico?)
4. Si no aprueba    → reintenta con ejemplos más específicos del estilo
5. Si aprueba       → entrega output final

OUTPUT (stdout):
  ORIGINAL  : [mensaje original]
  ESTILO    : [tipo solicitado]
  RESULTADO : [mensaje transformado]
  SCORE     : [autenticidad 1-10]
  INTENTOS  : [cuántos reintentos necesitó el after callback]
```

---

## Estilos disponibles

| tipo_transformacion | Descripción | Ejemplo |
|---|---|---|
| `flaite` | Jerga popular chilena urbana | "oye wn, pásame esa cuestión altiro" |
| `cuico` | Chileno de clase alta, formal y afectado | "¿Podrías hacerme llegar aquello a la brevedad?" |
| `politico` | Lenguaje político evasivo y grandilocuente | "En el marco de nuestro compromiso evaluaremos la situación" |
| `abuela` | Chilena mayor, cariñosa y con dichos | "Mijito, cuando puedas me mandas eso, no se te olvide" |
| `startup` | Mezcla de español e inglés tech | "Necesitamos alinear eso y hacer el handoff ASAP" |

---

## Arquitectura

```
main.py
└── ModismoAgent
    ├── before_callback   → valida input (tipo + msg)
    ├── gemini (DeepSeek vía API directa)  → transforma el mensaje
    └── after_callback    → evalúa autenticidad del output
                            dispara retry si score < 7
```

Un solo agente. La complejidad está en los callbacks, no en la delegación.

---

## Estructura de carpetas

```
adk-poc4-modismo-translator/
├── main.py                  # Entry point — parsea args y ejecuta el agente
├── agent.py                 # ModismoAgent con callbacks integrados
├── callbacks/
│   ├── __init__.py
│   ├── before_callback.py   # Valida tipo y msg antes de procesar
│   └── after_callback.py    # Evalúa autenticidad y decide retry
├── prompts/
│   ├── transform_prompt.txt # Prompt base de transformación
│   └── estilos/
│       ├── flaite.txt       # Ejemplos y contexto del estilo flaite
│       ├── cuico.txt
│       ├── politico.txt
│       ├── abuela.txt
│       └── startup.txt
├── .env.example
├── requirements.txt
└── README.md
```

---

## Cómo se ejecuta

```bash
# Instalar dependencias
pip install google-adk python-dotenv

# Configurar variables de entorno
cp .env.example .env

# Ejecutar
python main.py --tipo flaite --msg "necesito que me envíes el documento hoy"

# Ejemplos adicionales
python main.py --tipo cuico --msg "oye mándame eso"
python main.py --tipo politico --msg "no sé qué hacer con este problema"
python main.py --tipo abuela --msg "llámame cuando puedas"
python main.py --tipo startup --msg "hay que reunirse para ver el proyecto"
```

---

## Variables de entorno

```env
DEEPSEEK_API_KEY=your_deepseek_api_key
```

> ⚠️ Este PoC usa **DeepSeek vía API directa**, no Gemini. Configurar el agente ADK apuntando al endpoint de DeepSeek.

---

## Lógica de los callbacks

### before_callback
```
Valida:
  - tipo_transformacion está en la lista de estilos permitidos
  - msg_input no está vacío
  - msg_input tiene menos de 500 caracteres
Si falla → lanza error descriptivo, no llega al agente
```

### after_callback
```
Evalúa:
  - ¿El output contiene marcadores del estilo? (palabras clave, estructura)
  - ¿El significado del mensaje original se preservó?
  - Score de autenticidad 1-10
Si score < 7 → retry con prompt enriquecido (agrega ejemplos del estilo)
Si score >= 7 → aprueba y entrega
Máximo 3 intentos antes de entregar el mejor resultado obtenido
```

---

## Conceptos ADK que se practican

| Concepto | Dónde aparece |
|---|---|
| **Before callback** | Valida y sanitiza el input antes de procesar |
| **After callback** | Evalúa calidad del output y decide si aprueba |
| **Guardrails** | Lista blanca de estilos permitidos |
| **Retry con contexto** | El callback le dice al agente por qué falló |
| **Control flow** | El agente no entrega hasta que el callback aprueba |
| **Observability** | Log de cada intento con score y razón de retry |

---

## Restricciones de scope

- ❌ No construir UI
- ❌ No más de 1 agente
- ❌ No persistir historial (eso fue el PoC #3)
- ✅ Foco en que los callbacks intercepten y controlen el flujo real
- ✅ Los prompts por estilo van en archivos separados para facilitar iteración

---

## Definition of Done

- [ ] `before_callback` bloquea inputs inválidos con mensaje descriptivo
- [ ] El agente transforma correctamente los 5 estilos
- [ ] `after_callback` evalúa autenticidad con score numérico
- [ ] Si score < 7, el agente reintenta automáticamente
- [ ] Se loggea cada intento con su score y razón
- [ ] Funciona con `python main.py --tipo X --msg "Y"`
- [ ] Máximo 3 reintentos antes de entregar el mejor resultado

---

## Orden de avance actualizado

```
✅ 3 — Tool Use + Tool Chaining       (Daily Brief)
✅ 1 — Multi-agent + Delegation       (Academic Researcher)
✅ 2 — State + Memory + Sessions      (Knowledge Builder)
✅ 4 — Callbacks + Guardrails         (Modismo Translator)  ← este
⬜ 5 — Streaming + Live API           (Live API Agent)
```
