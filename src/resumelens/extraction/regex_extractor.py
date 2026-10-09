"""Etapa 1: extracción con expresiones regulares.

Solo EXTRAE cadenas que podrían ser datos o calificaciones. No decide si dos
cadenas son equivalentes (Etapa 2) ni si el candidato cumple un perfil (Etapa 3).

Salida: dict con las claves de contracts.STAGE1_KEYS (listas de cadenas únicas,
en orden de aparición, tal como aparecen en el texto).
"""
from __future__ import annotations

import json
import re

from resumelens.contracts import (
    CANONICAL, CATEGORY_TO_KEY, CASE_SENSITIVE_VARIANTS, STAGE1_KEYS, empty_stage1,
)


FIXED_PATTERNS: dict[str, tuple[str, str]] = {
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
    "education": (
        r"\b(?:Bachelor|Master|PhD|Ph\.D|Doctorate|B\.?Sc|M\.?Sc|Engineering|Engineer|"
        r"Ingenier[ií]a|Licenciatura|Maestr[ií]a|Especializaci[oó]n|Technician|Tecn[oó]log[oa]|"
        r"Associate degree|Diploma)\b(?:'s)?"
        r"(?:\s+(?:degree\s+)?(?:in|of|en|de)\s+(?!from\b|at\b)\w+(?:\s+(?!from\b|at\b|\d)\w+){0,3})?",
        "palabra de título académico (Bachelor, Master, PhD, Ingeniería...) seguida opcionalmente "
        "de 'in/of/en/de' y hasta 4 palabras del área de estudio (se corta en 'from'/'at')",
    ),
    "experience": (
        r"\b\d{1,2}\+?\s+(?:years?|a[nñ]os?)(?:\s+of\s+experience|\s+de\s+experiencia)?",
        "número de 1-2 dígitos (opcional '+') + 'year(s)'/'año(s)' y opcionalmente "
        "'of experience'/'de experiencia'",
    ),
}

EXTRA_TOOLS = ["GitHub", "GitLab", "Kubernetes", "Jenkins", "Linux", "Jira", "Postman", "AWS", "Azure"]
EXTRA_OTHER = ["deep learning", "data analysis", "unit testing", "CI/CD", "Agile", "Scrum"]


def _variant_regex(variant: str) -> str:
    # espacios del texto pueden ser varios espacios/saltos
    return re.escape(variant).replace(r"\ ", r"\s+")


def _build_list_regex(variants: list[str]) -> re.Pattern:
    """Alternancia de variantes, más largas primero, con límites de palabra.
    Las variantes ambiguas se aceptan solo con su mayúsculas exactas.
    """
    parts: list[str] = []
    for v in sorted(set(variants), key=lambda x: (-len(x), x)):
        if v in CASE_SENSITIVE_VARIANTS:
            parts += [f"(?-i:{re.escape(form)})" for form in CASE_SENSITIVE_VARIANTS[v]]
        else:
            parts.append(_variant_regex(v))
    body = "|".join(parts)
    return re.compile(rf"(?<![\w+#.-])(?:{body})(?![\w+#-])(?!\.com)", re.IGNORECASE)


def _variants_for_key(key: str) -> list[str]:
    out: list[str] = []
    for _tok, (cat, variants) in CANONICAL.items():
        if CATEGORY_TO_KEY[cat] == key:
            out += [v for v in variants if v not in CASE_SENSITIVE_VARIANTS
                    or CASE_SENSITIVE_VARIANTS[v]]
    if key == "tools":
        out += [t.lower() for t in EXTRA_TOOLS]
    if key == "other_qualifications":
        out += [t.lower() for t in EXTRA_OTHER]
    return out


LIST_PATTERNS: dict[str, re.Pattern] = {
    key: _build_list_regex(_variants_for_key(key))
    for key in ("languages", "frameworks", "databases", "tools", "other_qualifications")
}

_FIXED_COMPILED = {k: re.compile(rx, re.IGNORECASE if k in ("education",) else 0)
                   for k, (rx, _) in FIXED_PATTERNS.items()}

NAME_RE = re.compile(
    r"^[ \t]*([A-ZÁÉÍÓÚÑ][a-záéíóúñ']+(?:[ \t]+[A-ZÁÉÍÓÚÑ][a-záéíóúñ']+){1,3})[ \t]*$",
    re.MULTILINE,
)
NAME_SCAN_LINES = 6
# Líneas que parecen encabezados y no nombres
_NOT_A_NAME = re.compile(r"\b(?:Skills?|Experience|Education|Resume|Curriculum|Profile|Summary|Technical)\b", re.I)


def explain() -> dict[str, str]:
    """Explicación del lenguaje que reconoce cada regex (para el informe)."""
    out = {k: e for k, (_, e) in FIXED_PATTERNS.items()}
    out["name"] = ("línea sola de 2-4 palabras capitalizadas (letra mayúscula + minúsculas) "
                   f"dentro de las primeras {NAME_SCAN_LINES} líneas")
    for k in LIST_PATTERNS:
        out[k] = "alternancia de variantes conocidas (contracts.CANONICAL), delimitadas por no-letras"
    return out


def _unique(items) -> list[str]:
    seen, out = set(), []
    for s in items:
        s = s.strip()
        if s and s.lower() not in seen:
            seen.add(s.lower())
            out.append(s)
    return out


def extract(text: str) -> dict:
    """Devuelve el dict de la Etapa 1 (todas las claves de STAGE1_KEYS)."""
    result = empty_stage1()

    head = "\n".join(text.strip().splitlines()[:NAME_SCAN_LINES])
    result["name"] = _unique(
        m.group(1) for m in NAME_RE.finditer(head) if not _NOT_A_NAME.search(m.group(1))
    )[:1]

    for key, rx in _FIXED_COMPILED.items():
        result[key] = _unique(m.group(0) for m in rx.finditer(text))

    for key, rx in LIST_PATTERNS.items():
        result[key] = _unique(m.group(0) for m in rx.finditer(text))

    assert set(result) == set(STAGE1_KEYS)
    return result


def save(data: dict, path: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
