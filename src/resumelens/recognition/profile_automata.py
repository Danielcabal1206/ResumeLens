"""Etapa 3: reconocimiento de patrones de perfil con DFAs (pyformlang).

Cada perfil es un DFA  M = (Q, Σ, δ, q0, F)

  Q  : {q_start} ∪ {after_T | T ∈ Σ}. after_T = “el último token leído es T”.
  Σ  : tokens canónicos del perfil, en orden de slots (contracts.profile_alphabet).
  δ  : solo avanza en ese orden (índice j > i). No se puede saltar un slot
       obligatorio completo; los slots opcionales y las alternativas no usadas
       de un slot ya cubierto sí se pueden omitir.
  q0 : q_start
  F  : estados en los que todo slot obligatorio ya tiene algún token ≤ posición
       actual (no queda ningún slot obligatorio enteramente por delante).

Tipo: DFA. En cada estado hay a lo sumo una transición por símbolo, no hay λ,
y Σ es finito. El no-determinismo no aporta: el orden canónico de la Etapa 2
deja una sola lectura posible de cada secuencia.

El DFA rechaza desorden, duplicados y tokens ajenos porque no hay transición.
Por eso la Etapa 2 debe ordenar antes de clasificar.
"""
from __future__ import annotations

from pyformlang.finite_automaton import DeterministicFiniteAutomaton, State

from resumelens.contracts import PROFILES, canonical_sequence, profile_alphabet

START = "q_start"


def _slot_index_sets(profile: str) -> tuple[list[str], list[set[int]], list[bool]]:
    alphabet = profile_alphabet(profile)
    pos = {t: i for i, t in enumerate(alphabet)}
    idx_sets: list[set[int]] = []
    required: list[bool] = []
    for _name, opts, req in PROFILES[profile]:
        idx_sets.append({pos[t] for t in opts})
        required.append(req)
    return alphabet, idx_sets, required


def _jumps_over_required(i: int, j: int, idx_sets: list[set[int]], required: list[bool]) -> bool:
    skipped = set(range(i + 1, j))
    return any(req and idxs and idxs <= skipped for idxs, req in zip(idx_sets, required))


def _is_accepting(pos: int, idx_sets: list[set[int]], required: list[bool]) -> bool:
    return not any(req and idxs and all(k > pos for k in idxs) for idxs, req in zip(idx_sets, required))


def build_dfa(profile: str) -> DeterministicFiniteAutomaton:
    alphabet, idx_sets, required = _slot_index_sets(profile)
    states = {State(START)} | {State(f"after_{t}") for t in alphabet}
    dfa = DeterministicFiniteAutomaton(states=states)
    dfa.add_start_state(START)
    if _is_accepting(-1, idx_sets, required):
        dfa.add_final_state(START)
    for t in alphabet:
        if _is_accepting(alphabet.index(t), idx_sets, required):
            dfa.add_final_state(f"after_{t}")

    for j, dest in enumerate(alphabet):
        if not _jumps_over_required(-1, j, idx_sets, required):
            dfa.add_transition(START, dest, f"after_{dest}")
    for i, src in enumerate(alphabet):
        for j, dest in enumerate(alphabet):
            if j > i and not _jumps_over_required(i, j, idx_sets, required):
                dfa.add_transition(f"after_{src}", dest, f"after_{dest}")
    return dfa


AUTOMATA: dict[str, DeterministicFiniteAutomaton] = {p: build_dfa(p) for p in PROFILES}


def automaton_type(profile: str) -> str:
    dfa = AUTOMATA[profile]
    det = dfa.is_deterministic()
    return (
        "DFA: at most one δ(q, a) for each pair, no ε-transitions, finite Σ. "
        f"pyformlang.is_deterministic={det}."
    )


def explain_pattern(profile: str) -> str:
    slots = []
    for name, opts, req in PROFILES[profile]:
        mark = "required" if req else "optional"
        slots.append(f"{name} ({mark}): {' | '.join(opts)}")
    return (
        f"{profile} is the language of canonical sequences that cover every "
        f"required slot, stay in slot order, and may omit optional slots. "
        + " ".join(slots)
    )


def recognize(profile: str, sequence: list[str]) -> bool:
    return AUTOMATA[profile].accepts(sequence)


def classify_resume(tokens: list[str]) -> dict[str, dict]:
    out = {}
    for profile in PROFILES:
        seq = canonical_sequence(tokens, profile)
        out[profile] = {
            "result": "ACCEPTED" if recognize(profile, seq) else "REJECTED",
            "sequence": seq,
        }
    return out


def accepted_profiles(sequence: list[str]) -> list[str]:
    return [p for p in PROFILES if recognize(p, sequence)]


def formal_definition(profile: str) -> dict:
    dfa = AUTOMATA[profile]
    delta = {}
    for src, by_sym in dfa._transition_function.to_dict().items():
        for sym, dest in by_sym.items():
            delta[(str(src), str(sym))] = str(dest)
    starts = [str(s) for s in dfa.start_states]
    return {
        "Q": sorted(str(s) for s in dfa.states),
        "Sigma": list(profile_alphabet(profile)),
        "delta": delta,
        "q0": starts[0] if starts else START,
        "F": sorted(str(s) for s in dfa.final_states),
    }


def export_dot(profile: str, path: str) -> None:
    AUTOMATA[profile].write_as_dot(path)


def export_all_dots(directory: str) -> list[str]:
    from pathlib import Path

    out = Path(directory)
    out.mkdir(parents=True, exist_ok=True)
    written = []
    for profile in PROFILES:
        path = str(out / f"dfa_{profile.lower()}.dot")
        export_dot(profile, path)
        written.append(path)
    return written
