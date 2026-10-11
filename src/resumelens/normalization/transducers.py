"""Etapa 2: normalización con transductores de estado finito (pyformlang).

Modelo formal  M = (Q, Σ, Γ, δ, ω, q0, F)
  Q  : estados. q0 inicial y un estado por cada prefijo de cada variante.
  Σ  : alfabeto de entrada = caracteres que aparecen en las variantes.
  Γ  : alfabeto de salida = tokens canónicos (JAVASCRIPT, REACT, ...).
  δ  : δ(q, c) = q'   (transición por carácter; es un trie por token)
  ω  : ω(q, c, q') = [TOKEN] en la PRIMERA transición de cada variante, y
       [] (cadena vacía) en las demás. Así el token se emite una sola vez
       aunque una variante sea prefijo de otra (react / reactjs).
  q0 : estado inicial común.
  F  : un estado final por cada variante completa.

Hay un transductor por categoría (FRONTEND, BACKEND, DATABASE, ...) para el
informe y los diagramas, y uno global (union) para el pipeline.
"""
from __future__ import annotations

from pyformlang.fst import FST

from resumelens.contracts import (
    CANONICAL, QUALIFICATION_KEYS, VARIANT_TO_TOKEN, canonical_sequence, tokens_of_category,
)

START = "q0"


def preprocess(raw: str) -> str:
    """Minúsculas, recorta y colapsa espacios. Va ANTES del transductor, de modo
    que Σ solo necesita caracteres en minúscula."""
    return " ".join(raw.lower().split())


def build_fst(tokens: list[str]) -> FST:
    """Construye el transductor (trie) para un conjunto de tokens canónicos.
    Los estados se llaman TOKEN_k (k = número del nodo del trie); evitar ':' en
    los nombres porque rompe la exportación a DOT."""
    fst = FST()
    fst.add_start_state(START)
    for token in tokens:
        _cat, variants = CANONICAL[token]
        node_of: dict[str, str] = {"": START}   # prefijo -> estado (trie por token)
        for variant in variants:
            for i, ch in enumerate(variant):
                prefix, nxt = variant[:i], variant[: i + 1]
                if nxt not in node_of:
                    node_of[nxt] = f"{token}_{len(node_of)}"
                    out = [token] if i == 0 else []
                    fst.add_transition(node_of[prefix], ch, node_of[nxt], out)
            fst.add_final_state(node_of[variant])
    return fst


CATEGORIES = sorted({cat for cat, _ in CANONICAL.values()})
FSTS: dict[str, FST] = {cat: build_fst(tokens_of_category(cat)) for cat in CATEGORIES}
GLOBAL_FST: FST = build_fst(list(CANONICAL))


def normalize_term(raw: str) -> str | None:
    """'Node.js' -> 'NODE_JS'. Devuelve None si el término no se reconoce."""
    word = preprocess(raw)
    outputs = {" ".join(map(str, o)) for o in GLOBAL_FST.translate(list(word))}
    outputs.discard("")
    if len(outputs) == 1:
        return outputs.pop()
    return None  # no reconocido (o, si fuera ambiguo, se rechaza)


def normalize_all(stage1: dict) -> list[str]:
    """Dict de la Etapa 1 -> lista de tokens canónicos, sin duplicados, en orden
    de aparición. Términos no reconocidos se ignoran."""
    tokens: list[str] = []
    for key in QUALIFICATION_KEYS:
        for raw in stage1.get(key, []):
            tok = normalize_term(raw)
            if tok and tok not in tokens:
                tokens.append(tok)
    return tokens


def order_for_profile(tokens: list[str], profile: str) -> list[str]:
    """Orden canónico del perfil (evita depender del orden del CV)."""
    return canonical_sequence(tokens, profile)


# ---------------------------------------------------------------------------
# Utilidades para el informe: definición formal y diagrama
# ---------------------------------------------------------------------------
def formal_definition(fst: FST) -> dict:
    """Devuelve la 7-tupla de un transductor en formato legible."""
    delta, omega = {}, {}
    for (s_from, sym), targets in _transitions(fst):
        for s_to, out in targets:
            delta.setdefault((s_from, sym), set()).add(s_to)
            omega[(s_from, sym, s_to)] = out
    return {
        "Q": sorted(map(str, fst.states)),
        "Sigma": sorted(map(str, fst.input_symbols)),
        "Gamma": sorted(map(str, fst.output_symbols)),
        "delta": delta,
        "omega": omega,
        "q0": [str(s) for s in fst.start_states],
        "F": sorted(map(str, fst.final_states)),
    }


def _transitions(fst: FST):
    """Itera (estado, símbolo) -> [(destino, salida)] tolerando variaciones de API."""
    t = fst.transitions
    if isinstance(t, dict):
        for key, targets in t.items():
            yield key, [(s, list(o)) for s, o in targets]
    else:
        for key, targets in t:
            yield key, [(s, list(o)) for s, o in targets]


def export_dot(fst: FST, path: str) -> None:
    """Escribe el diagrama en formato DOT (renderizar con graphviz:  dot -Tpng f.dot -o f.png)."""
    fst.write_as_dot(path)


def export_all_dots(directory: str) -> list[str]:
    """Exporta el FST global y un FST por categoría. Devuelve las rutas escritas."""
    from pathlib import Path

    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for name, fst in [("GLOBAL", GLOBAL_FST), *FSTS.items()]:
        path = str(out / f"fst_{name.lower()}.dot")
        export_dot(fst, path)
        written.append(path)
    return written
