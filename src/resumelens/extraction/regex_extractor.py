"""Etapa 1 (parte A): extracción con expresiones regulares.

Solo EXTRAE cadenas que podrían ser calificaciones. No decide si dos cadenas
son equivalentes (Etapa 2) ni si el candidato cumple un perfil (Etapa 3).
"""
import re
import json

# nombre -> (regex, explicación del lenguaje que reconoce)
PATTERNS = {
    # --- Contacto ---
    "email": (
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9-]+(?:\.[A-Za-z0-9-]+)*\.[A-Za-z]{2,}",
        "usuario (letras, dígitos, . _ % + -) + '@' + dominio con punto y TLD de 2+ letras",
    ),
    "phone": (
        r"(?<!\d)(?:\+\d{1,3}[\s-]?)?(?:\(\d{2,4}\)[\s-]?)?\d{3}[\s-]?\d{3,4}(?:[\s-]?\d{2,4})?(?!\d)",
        "prefijo opcional '+57', código opcional entre paréntesis y 8-12 dígitos con espacios o guiones",
    ),
    "linkedin": (
        r"(?:https?://)?(?:www\.)?linkedin\.com/in/[A-Za-z0-9_-]+/?",
        "URL de perfil: linkedin.com/in/ seguido de un identificador",
    ),
    "github": (
        r"(?:https?://)?(?:www\.)?github\.com/[A-Za-z0-9_-]+/?",
        "URL de GitHub: github.com/ seguido del usuario",
    ),
    # --- Tecnologías ---
    "languages": (
        r"(?<![\w+#])(?:JavaScript|Javascript|JS|TypeScript|TS|Python|Java|C\+\+|C#|Go|Rust|PHP|Ruby|Kotlin|Swift|R|SQL)(?![\w+#])",
        "nombre o abreviatura de un lenguaje, delimitado por no-letras (así 'Java' no coincide dentro de 'JavaScript')",
    ),
    "frameworks": (
        r"\b(?:React(?:\.?js)?|Angular(?:\.?js)?|Vue(?:\.?js)?|Node\.?js|Express(?:\.?js)?|Django|Flask|FastAPI|"
        r"Spring\s?Boot|Pandas|NumPy|Scikit[-\s]?learn|sklearn|Tensor\s?Flow|Py\s?Torch|Keras|Matplotlib)\b",
        "framework o librería; admite variantes con/sin punto, guion o espacio (React.js, ReactJS, scikit learn...)",
    ),
    "databases": (
        r"\b(?:PostgreSQL|Postgres|MySQL|MariaDB|SQLite|MongoDB|Mongo|Redis|Oracle|SQL\s?Server|Cassandra|Firebase)\b",
        "nombre de un motor de base de datos SQL o NoSQL",
    ),
}

_COMPILED = {k: re.compile(rx, re.IGNORECASE) for k, (rx, _) in PATTERNS.items()}


def extract(text: str) -> dict:
    """Devuelve {categoría: [cadenas únicas en orden de aparición]}."""
    result = {}
    for name, rx in _COMPILED.items():
        seen, found = set(), []
        for m in rx.finditer(text):
            s = m.group(0).strip()
            if s.lower() not in seen:
                seen.add(s.lower())
                found.append(s)
        result[name] = found
    return result


def save(data: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)