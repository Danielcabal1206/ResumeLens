# ResumeLens: Formal Language-Based Resume Screening

ResumeLens procesa currículums en texto plano y determina si las calificaciones **explícitas** en el currículum satisfacen un patrón formal asociado a un perfil profesional. No ordena candidatos ni toma decisiones de contratación.

```
texto del CV → [1 Regex] → cadenas → [2 FST] → tokens canónicos ordenados → [3 Autómatas] → perfil + ACCEPTED/REJECTED → [4 DSL textX] → HTML/Markdown
```

| Etapa | Modelo formal | Herramienta | Qué hace |
|---|---|---|---|
| 1. Extracción | Expresiones regulares | `re` | Detecta cadenas que pueden ser datos o calificaciones |
| 2. Normalización | Transductores de estado finito | `pyformlang` | Convierte variantes (`JS`, `Javascript`) a una forma canónica (`JAVASCRIPT`) y las ordena |
| 3. Reconocimiento | Autómatas finitos (DFA/NFA/ε-NFA) | `pyformlang` | Decide si la secuencia canónica cumple el patrón de un perfil |
| 4. Perfil del candidato | Gramática libre de contexto (DSL) | `textX` | Valida el perfil estructurado y genera la visualización HTML/Markdown |

## Estado del proyecto (entrega esta noche)

Avance global estimado: **~90%**. Código de las 4 etapas + pipeline listos. Falta sobre todo tests EBNF de la DSL y la presentación oral.

| Fase | Avance | Estado | Hecho | Pendiente |
|---|---|---|---|---|
| **1. Extracción (regex)** | **100%** | Completo | Contacto, nombre, skills, educación, experiencia; `extract` / `explain` / JSON; tests | — |
| **2. Normalización (FST)** | **100%** | Completo | Transductores pyformlang; 7-tupla; DOT; orden canónico; tests | — |
| **3. Autómatas** | **100%** | Completo | 4 DFA en pyformlang; 5-tupla; tipo DFA justificado; DOT en `docs/diagrams/`; `classify_resume`; tests | — |
| **4. DSL textX** | **~85%** | Casi listo | Gramática `.tx`, validador, HTML/MD, pipeline | Tests extra de gramática / EBNF en el informe |
| **Pipeline** | **100%** | Completo | Une 1→2→DFA→DSL→HTML; CVs de ejemplo | — |
| **UI** | **CLI 100%** | Completo | `python main.py data/resumes/fullstack.txt` | — |
| **Literatura** | **100%** | Completo | `docs/literature_review.md` | — |
| **Diseño de módulos** | **100%** | Completo | Contratos, README, I/O por etapa | — |
| **Diagramas** | **100%** | Completo | DOT de FST y DFA en `docs/diagrams/` | PNG en póster si Graphviz está instalado |
| **Póster** | **100%** | Completo | Entregable del equipo | — |
| **Presentación 10 min EN** | **~0%** | Pendiente | — | Guion oral en inglés |

## Ejecución

```bash
pip install -r requirements.txt
python main.py data/resumes/fullstack.txt
pytest
```

Salida en `output/`: JSON (Etapa 1), `.rl` (DSL), Markdown y HTML.

Currículums de ejemplo: `data/resumes/{fullstack,ml_engineer,backend,data_analyst,incomplete}.txt`.

## Contratos entre etapas

### Salida de la Etapa 1 (entrada de la Etapa 2 y 4)

Diccionario con claves fijas. Si una categoría no aparece, su valor es `[]`.

```python
{
    "name": [],
    "email": [],
    "phone": [],
    "linkedin": [],
    "github": [],
    "languages": [],
    "frameworks": [],
    "databases": [],
    "education": [],
    "experience": [],
    "tools": [],
    "other_qualifications": [],
}
```

Cada valor es una lista de cadenas únicas, en orden de aparición, **tal como aparecen en el texto** (sin normalizar).

La Etapa 2 recibe `languages + frameworks + databases + tools + other_qualifications`. El resto va a la Etapa 4.

### Tokens canónicos (salida de la Etapa 2, alfabeto Σ de la Etapa 3)

Fuente de verdad: `src/resumelens/contracts.py` (`CANONICAL`). Tokens en MAYÚSCULAS con guion bajo.

| Categoría | Token canónico | Variantes (ejemplos) |
|---|---|---|
| Lenguaje | `JAVASCRIPT` | JS, Javascript, JavaScript |
| Lenguaje | `TYPESCRIPT` | TS, Typescript |
| Lenguaje | `PYTHON` | python, Py |
| Lenguaje | `JAVA` | java |
| Lenguaje | `SQL` | sql |
| Lenguaje | `R` | R |
| Frontend | `REACT` | React.js, ReactJS, React |
| Frontend | `ANGULAR` | Angular, AngularJS, Angular.js |
| Frontend | `VUE` | Vue, Vue.js, VueJS |
| Backend | `NODE_JS` | NodeJS, Node.js, node |
| Backend | `EXPRESS` | Express, Express.js |
| Backend | `DJANGO` | Django |
| Backend | `SPRING_BOOT` | Spring Boot, SpringBoot |
| Backend | `FLASK` | Flask |
| Base de datos | `POSTGRESQL` | Postgres, PostgreSQL |
| Base de datos | `MYSQL` | MySQL |
| Base de datos | `MONGODB` | Mongo, MongoDB |
| Base de datos | `SQLITE` | SQLite |
| API | `REST_API` | REST, REST API, RESTful API, REST APIs |
| Control de versiones | `GIT` | git, Git |
| Datos / ML | `PANDAS` | pandas, Pandas |
| Datos / ML | `NUMPY` | numpy, NumPy |
| Datos / ML | `SCIKIT_LEARN` | sklearn, scikit learn, Scikit-learn |
| Datos / ML | `TENSORFLOW` | Tensor Flow, TensorFlow |
| Datos / ML | `PYTORCH` | Py Torch, PyTorch |
| Datos / ML | `ML_MODEL_DEVELOPMENT` | machine learning, ML model development |
| Visualización | `MATPLOTLIB` | matplotlib |
| Visualización | `POWER_BI` | Power BI, PowerBI |
| Visualización | `TABLEAU` | Tableau |
| DevOps | `DOCKER` | docker, Docker |

Cualquier extensión se agrega **solo** en `contracts.py`.

## Perfiles profesionales

Cada perfil es una secuencia de slots en orden fijo (orden canónico de la Etapa 2). Un slot puede ser obligatorio u opcional.

### 1. Full Stack Developer (predefinido)

Lenguaje → Frontend → Backend → Base de datos → API? → Git

Ejemplo aceptado: `JAVASCRIPT REACT NODE_JS POSTGRESQL GIT`

### 2. Machine Learning Engineer (predefinido)

Python → Pandas/NumPy → Scikit-learn/TensorFlow/PyTorch → ML_DEV? → SQL/Postgres/MySQL → Git

Ejemplo aceptado: `PYTHON PANDAS TENSORFLOW POSTGRESQL GIT`

### 3. Backend Developer (equipo, ingeniería de software)

Lenguaje → framework backend → base de datos → REST_API → Docker? → Git

Ejemplo aceptado: `JAVA SPRING_BOOT POSTGRESQL REST_API DOCKER GIT`

### 4. Data Analyst (equipo, IA/datos)

Python/R → Pandas/NumPy → Matplotlib/Power BI/Tableau → SQL/Postgres/MySQL → Git?

Ejemplo aceptado: `PYTHON PANDAS MATPLOTLIB SQL`

Definición ejecutable: `PROFILES` en `contracts.py`.

## Estructura del proyecto

```
ResumeLens/
├── data/resumes/
├── docs/
│   ├── literature_review.md
│   └── diagrams/              # DOT de FST y DFA
├── output/
├── src/
│   ├── dsl/
│   └── resumelens/
│       ├── contracts.py
│       ├── extraction/regex_extractor.py
│       ├── normalization/transducers.py
│       ├── recognition/profile_automata.py
│       └── pipeline.py
├── test/
├── main.py
├── requirements.txt
└── README.md
```

## Equipo

| Área | Estado |
|---|---|
| Etapa 1, 2, 3, pipeline, literatura, diagramas | Listo |
| DSL (EBNF en el informe) y presentación 10 min EN | Cierre del equipo |
