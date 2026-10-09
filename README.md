# ResumeLens: Formal Language-Based Resume Screening

ResumeLens procesa currículums en texto plano y determina si las calificaciones **explícitas** en el currículum satisfacen un patrón formal asociado a un perfil profesional. No ordena candidatos ni toma decisiones de contratación.

Cada etapa del pipeline usa un modelo de lenguajes formales distinto:

| Etapa | Modelo formal | Herramienta | Qué hace |
|---|---|---|---|
| 1. Extracción | Expresiones regulares | `re` | Detecta cadenas que pueden ser datos o calificaciones |
| 2. Normalización | Transductores de estado finito | `pyformlang` | Convierte variantes (`JS`, `Javascript`) a una forma canónica (`JAVASCRIPT`) y las ordena |
| 3. Reconocimiento | Autómatas finitos (DFA/NFA/ε-NFA) | `pyformlang` | Decide si la secuencia canónica cumple el patrón de un perfil |
| 4. Perfil del candidato | Gramática libre de contexto (DSL) | `textX` | Valida el perfil estructurado y genera la visualización HTML/Markdown |

```
texto del CV → [1 Regex] → cadenas → [2 FST] → tokens canónicos ordenados → [3 Autómatas] → perfil + ACCEPTED/REJECTED → [4 DSL textX] → HTML/Markdown
```

## Estado del proyecto

| Etapa | Estado | Hecho | Falta |
|---|---|---|---|
| 1. Regex |  Completo | Contacto (email, teléfono, LinkedIn, GitHub), lenguajes, frameworks, bases de datos, `extract()` y guardado JSON | Educación, experiencia, herramientas, otras calificaciones, nombre; explicación de cada regex; tests |
| 2. Transductores |  Completo | Archivo `transducers.py` creado | Transformaciones propias, 7-tupla formal, diagramas, implementación con pyformlang, orden canónico, tests |
| 3. Autómatas |  Pendiente | Archivo `profile_automata.py` creado | 4 patrones, tipo de autómata justificado, 5-tupla, diagramas, implementación, tests |
| 4. DSL textX |  Pendiente | Carpeta `dsl/` creada | Gramática EBNF, `.tx`, validador, generador HTML/MD, tests |
| Pipeline / UI |  Pendiente | `pipeline.py` y `main.py` creados | Unir las 4 etapas e interfaz |
| Documentación |  Pendiente | Este README | Literatura, diseño, casos de prueba, póster, presentación (10 min, en inglés) 

Las etapas 2, 3 y 4 pueden desarrollarse **en paralelo** usando los contratos definidos abajo.

## Contratos entre etapas

### Salida de la Etapa 1 (entrada de la Etapa 2 y 4)

Diccionario con estas claves fijas. Si una categoría no se encuentra o aún no está implementada, su valor es una lista vacía.

```python
{
    "name": [],                 # nombre del candidato (por implementar)
    "email": [],
    "phone": [],
    "linkedin": [],
    "github": [],
    "languages": [],            # JS, Python, Java...
    "frameworks": [],           # React.js, sklearn, Tensor Flow...
    "databases": [],            # Postgres, MongoDB...
    "education": [],            # títulos académicos (por implementar)
    "experience": [],           # "3 years of experience" (por implementar)
    "tools": [],                # Git, Docker... (por implementar)
    "other_qualifications": []  # REST API, machine learning model development (por implementar)
}
```

Cada valor es una lista de cadenas únicas, en orden de aparición, tal como aparecen en el texto (sin normalizar).

La Etapa 2 recibe como entrada las claves `languages + frameworks + databases + tools + other_qualifications`. El resto de claves va directo a la Etapa 4.

### Tokens canónicos (salida de la Etapa 2, alfabeto Σ de la Etapa 3)

| Categoría | Token canónico | Variantes que normaliza (ejemplos) |
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

Los tokens son MAYÚSCULAS con guion bajo. Cualquier extensión debe agregarse a esta tabla antes de usarse en la Etapa 2 o 3.

## Perfiles profesionales

Cada perfil se define como una secuencia de **categorías** (slots) en orden fijo. Ese orden es el **orden canónico** que la Etapa 2 aplica antes de enviar la secuencia a los autómatas. Un slot puede ser obligatorio (1 de varias opciones) u opcional (`?`).

### 1. Full Stack Developer (predefinido)
Orden: Lenguaje → Frontend → Backend → Base de datos → API → Control de versiones

| Slot | Opciones | Obligatorio |
|---|---|---|
| Lenguaje | `JAVASCRIPT`, `TYPESCRIPT` | Sí |
| Frontend | `REACT`, `ANGULAR`, `VUE` | Sí |
| Backend | `NODE_JS`, `EXPRESS`, `DJANGO`, `SPRING_BOOT` | Sí |
| Base de datos | `POSTGRESQL`, `MYSQL`, `MONGODB`, `SQLITE` | Sí |
| API | `REST_API` | No |
| Control de versiones | `GIT` | Sí |

Ejemplo aceptado: `JAVASCRIPT REACT NODE_JS POSTGRESQL GIT`

### 2. Machine Learning Engineer (predefinido)
Orden: Lenguaje → Manejo de datos → Modelos → Desarrollo ML → Base de datos → Control de versiones

| Slot | Opciones | Obligatorio |
|---|---|---|
| Lenguaje | `PYTHON` | Sí |
| Manejo de datos | `PANDAS`, `NUMPY` (una o ambas) | Sí |
| Modelos | `SCIKIT_LEARN`, `TENSORFLOW`, `PYTORCH` (una o más, en ese orden) | Sí |
| Desarrollo ML | `ML_MODEL_DEVELOPMENT` | No |
| Base de datos | `SQL`, `POSTGRESQL`, `MYSQL` | Sí |
| Control de versiones | `GIT` | Sí |

Ejemplo aceptado: `PYTHON PANDAS TENSORFLOW POSTGRESQL GIT`

### 3. Backend Developer (propuesto por el equipo, ingeniería de software)
Orden: Lenguaje → Framework backend → Base de datos → API → Contenedores → Control de versiones

| Slot | Opciones | Obligatorio |
|---|---|---|
| Lenguaje | `PYTHON`, `JAVA`, `JAVASCRIPT`, `TYPESCRIPT` | Sí |
| Framework backend | `DJANGO`, `FLASK`, `SPRING_BOOT`, `NODE_JS`, `EXPRESS` | Sí |
| Base de datos | `POSTGRESQL`, `MYSQL`, `MONGODB`, `SQLITE` | Sí |
| API | `REST_API` | Sí |
| Contenedores | `DOCKER` | No |
| Control de versiones | `GIT` | Sí |

Ejemplo aceptado: `JAVA SPRING_BOOT POSTGRESQL REST_API DOCKER GIT`

### 4. Data Analyst (propuesto por el equipo, IA/datos)
Orden: Lenguaje → Manejo de datos → Visualización → Base de datos → Control de versiones

| Slot | Opciones | Obligatorio |
|---|---|---|
| Lenguaje | `PYTHON`, `R` | Sí |
| Manejo de datos | `PANDAS`, `NUMPY` | Sí |
| Visualización | `MATPLOTLIB`, `POWER_BI`, `TABLEAU` | Sí |
| Base de datos | `SQL`, `POSTGRESQL`, `MYSQL` | Sí |
| Control de versiones | `GIT` | No |

Ejemplo aceptado: `PYTHON PANDAS MATPLOTLIB SQL`

> **Nota:** los perfiles 3 y 4 son una **propuesta provisional**. El enunciado indica que los requisitos de los perfiles propios se entregan por separado; ajustar esta sección cuando se tengan.

## Estructura del proyecto

```
ResumeLens/
├── data/
│   ├── profiles/        # definición de los 4 perfiles
│   └── resumes/         # currículums de ejemplo
├── docs/                # diseño, diagramas, póster, literatura
├── src/
│   ├── dsl/                    # Etapa 4: gramática textX, validador, generador HTML/MD
│   └── resumelens/
│       ├── extraction/regex_extractor.py     # Etapa 1
│       ├── normalization/transducers.py      # Etapa 2
│       ├── recognition/profile_automata.py   # Etapa 3
│       └── pipeline.py
├── test/
├── main.py
├── requirements.txt     # pyformlang, textx, graphviz
└── README.md
```

## Ejecución

```bash
pip install -r requirements.txt
python main.py
```

## Equipo y responsabilidades

| Integrante | Responsabilidad principal |
|---|---|
| 1 | Etapa 1 (regex) y Etapa 2 (transductores) |
| 2 | Etapa 3 (autómatas) y pipeline |
| 3 | Etapa 4 (textX + visualización), literatura y póster |

Cada integrante escribe los tests, el diseño y los diagramas de su propia etapa.