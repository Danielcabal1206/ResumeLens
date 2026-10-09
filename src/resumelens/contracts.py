"""Contratos compartidos entre las 4 etapas de ResumeLens.

FUENTE ÚNICA DE VERDAD. Si hay que agregar una tecnología, una variante o
cambiar un perfil, se hace SOLO aquí. Las etapas 1, 2 y 3 se construyen a
partir de este módulo.

  Etapa 1 (regex)  -> dict con STAGE1_KEYS
  Etapa 2 (FST)    -> lista de tokens canónicos (CANONICAL) ordenada por perfil
  Etapa 3 (FA)     -> alfabeto = tokens canónicos; patrón = PROFILES
  Etapa 4 (textX)  -> usa el dict de la Etapa 1 + resultado de la Etapa 3
"""
from __future__ import annotations


STAGE1_KEYS = (
    "name", "email", "phone", "linkedin", "github",
    "languages", "frameworks", "databases",
    "education", "experience", "tools", "other_qualifications",
)

QUALIFICATION_KEYS = ("languages", "frameworks", "databases", "tools", "other_qualifications")


def empty_stage1() -> dict:
    """Diccionario de Etapa 1 vacío (todas las claves, listas vacías)."""
    return {k: [] for k in STAGE1_KEYS}



CANONICAL: dict[str, tuple[str, list[str]]] = {
    # Lenguajes
    "JAVASCRIPT": ("LANGUAGE", ["javascript", "js", "java script"]),
    "TYPESCRIPT": ("LANGUAGE", ["typescript", "ts", "type script"]),
    "PYTHON":     ("LANGUAGE", ["python", "py", "python3", "python 3"]),
    "JAVA":       ("LANGUAGE", ["java"]),
    "SQL":        ("LANGUAGE", ["sql"]),
    "R":          ("LANGUAGE", ["r"]),
    # Frontend
    "REACT":   ("FRONTEND", ["react", "react.js", "reactjs", "react js"]),
    "ANGULAR": ("FRONTEND", ["angular", "angular.js", "angularjs", "angular js"]),
    "VUE":     ("FRONTEND", ["vue", "vue.js", "vuejs", "vue js"]),
    # Backend
    "NODE_JS":     ("BACKEND", ["node", "node.js", "nodejs", "node js"]),
    "EXPRESS":     ("BACKEND", ["express", "express.js", "expressjs"]),
    "DJANGO":      ("BACKEND", ["django"]),
    "SPRING_BOOT": ("BACKEND", ["spring boot", "springboot", "spring-boot"]),
    "FLASK":       ("BACKEND", ["flask"]),
    # Bases de datos
    "POSTGRESQL": ("DATABASE", ["postgresql", "postgres", "postgre sql", "psql"]),
    "MYSQL":      ("DATABASE", ["mysql", "my sql"]),
    "MONGODB":    ("DATABASE", ["mongodb", "mongo", "mongo db"]),
    "SQLITE":     ("DATABASE", ["sqlite", "sqlite3", "sql lite"]),
    # API
    "REST_API": ("API", ["rest", "rest api", "rest apis", "restful", "restful api",
                         "restful apis", "rest-api"]),
    # Control de versiones / DevOps
    "GIT":    ("VERSION_CONTROL", ["git"]),
    "DOCKER": ("DEVOPS", ["docker"]),
    # Datos y ML
    "PANDAS":       ("DATA_LIB", ["pandas"]),
    "NUMPY":        ("DATA_LIB", ["numpy", "num py"]),
    "SCIKIT_LEARN": ("ML_LIB", ["scikit-learn", "scikit learn", "sklearn", "scikitlearn"]),
    "TENSORFLOW":   ("ML_LIB", ["tensorflow", "tensor flow"]),
    "PYTORCH":      ("ML_LIB", ["pytorch", "py torch", "torch"]),
    "ML_MODEL_DEVELOPMENT": ("ML_DEV", [
        "machine learning", "machine-learning", "ml", "machine learning models",
        "machine learning model development", "ml model development"]),
    # Visualización
    "MATPLOTLIB": ("VIZ_LIB", ["matplotlib", "mat plotlib"]),
    "POWER_BI":   ("VIZ_TOOL", ["power bi", "powerbi", "power-bi"]),
    "TABLEAU":    ("VIZ_TOOL", ["tableau"]),
}

CATEGORY_TO_KEY = {
    "LANGUAGE": "languages",
    "FRONTEND": "frameworks", "BACKEND": "frameworks", "DATA_LIB": "frameworks",
    "ML_LIB": "frameworks", "VIZ_LIB": "frameworks",
    "DATABASE": "databases",
    "VERSION_CONTROL": "tools", "DEVOPS": "tools", "VIZ_TOOL": "tools",
    "API": "other_qualifications", "ML_DEV": "other_qualifications",
}

CASE_SENSITIVE_VARIANTS = {
    "r": ["R"], "go": ["Go"], "js": ["JS"], "ts": ["TS"], "ml": ["ML"],
    "rest": ["REST"], "express": ["Express"], "py": [], "torch": ["Torch"],
}

VARIANT_TO_TOKEN: dict[str, str] = {}
for _tok, (_cat, _vars) in CANONICAL.items():
    for _v in _vars:
        assert _v == _v.lower(), f"variante no está en minúsculas: {_v!r}"
        assert _v not in VARIANT_TO_TOKEN, f"variante repetida: {_v!r}"
        VARIANT_TO_TOKEN[_v] = _tok


def tokens_of_category(category: str) -> list[str]:
    return [t for t, (c, _) in CANONICAL.items() if c == category]



PROFILES: dict[str, list[tuple[str, list[str], bool]]] = {
    "FULL_STACK_DEVELOPER": [
        ("language",  ["JAVASCRIPT", "TYPESCRIPT"], True),
        ("frontend",  ["REACT", "ANGULAR", "VUE"], True),
        ("backend",   ["NODE_JS", "EXPRESS", "DJANGO", "SPRING_BOOT"], True),
        ("database",  ["POSTGRESQL", "MYSQL", "MONGODB", "SQLITE"], True),
        ("api",       ["REST_API"], False),
        ("version",   ["GIT"], True),
    ],
    "MACHINE_LEARNING_ENGINEER": [
        ("language",  ["PYTHON"], True),
        ("data",      ["PANDAS", "NUMPY"], True),
        ("models",    ["SCIKIT_LEARN", "TENSORFLOW", "PYTORCH"], True),
        ("ml_dev",    ["ML_MODEL_DEVELOPMENT"], False),
        ("database",  ["SQL", "POSTGRESQL", "MYSQL"], True),
        ("version",   ["GIT"], True),
    ],
    # --- Perfiles propios del equipo (PROVISIONALES, ajustar al enunciado) ---
    "BACKEND_DEVELOPER": [
        ("language",  ["PYTHON", "JAVA", "JAVASCRIPT", "TYPESCRIPT"], True),
        ("backend",   ["DJANGO", "FLASK", "SPRING_BOOT", "NODE_JS", "EXPRESS"], True),
        ("database",  ["POSTGRESQL", "MYSQL", "MONGODB", "SQLITE"], True),
        ("api",       ["REST_API"], True),
        ("devops",    ["DOCKER"], False),
        ("version",   ["GIT"], True),
    ],
    "DATA_ANALYST": [
        ("language",  ["PYTHON", "R"], True),
        ("data",      ["PANDAS", "NUMPY"], True),
        ("viz",       ["MATPLOTLIB", "POWER_BI", "TABLEAU"], True),
        ("database",  ["SQL", "POSTGRESQL", "MYSQL"], True),
        ("version",   ["GIT"], False),
    ],
}

for _p, _slots in PROFILES.items():
    for _name, _opts, _req in _slots:
        for _t in _opts:
            assert _t in CANONICAL, f"{_p}/{_name}: token desconocido {_t}"


def profile_alphabet(profile: str) -> list[str]:
    """Alfabeto Σ de un perfil (en orden canónico). Útil para los autómatas."""
    return [t for _, opts, _ in PROFILES[profile] for t in opts]


def canonical_sequence(tokens: list[str], profile: str) -> list[str]:
    """Filtra los tokens relevantes al perfil, quita duplicados y los ordena en
    el orden canónico del perfil (slot por slot, y dentro del slot en el orden
    en que está declarado). Los tokens ajenos al perfil se descartan.
    """
    wanted = set(tokens)
    return [t for t in profile_alphabet(profile) if t in wanted]


def profile_accepts(profile: str, sequence: list[str]) -> bool:
    """ORÁCULO en Python puro: ¿la secuencia canónica cumple el perfil?
    Sirve para verificar que los autómatas de la Etapa 3 coinciden con la
    especificación. `sequence` debe venir de canonical_sequence().
    """
    if sequence != canonical_sequence(sequence, profile):
        return False
    present = set(sequence)
    return all(
        (not required) or any(t in present for t in opts)
        for _, opts, required in PROFILES[profile]
    )


def classify(tokens: list[str]) -> dict[str, bool]:
    """Evalúa los 4 perfiles con el oráculo. {perfil: ACCEPTED?}"""
    return {p: profile_accepts(p, canonical_sequence(tokens, p)) for p in PROFILES}
