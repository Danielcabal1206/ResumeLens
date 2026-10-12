"""Etapa 3: los autómatas deben reconocer EXACTAMENTE lo que dice la especificación
(contracts.PROFILES), verificado contra el oráculo en Python puro."""
from itertools import combinations

import pytest

from resumelens.contracts import PROFILES, canonical_sequence, profile_accepts, profile_alphabet
from resumelens.recognition.profile_automata import (
    AUTOMATA, accepted_profiles, automaton_type, classify_resume, explain_pattern,
    export_dot, formal_definition, recognize,
)

PROFILE_NAMES = list(PROFILES)


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_dfa_matches_oracle_on_every_subset(profile):
    """Para TODOS los subconjuntos del alfabeto (en orden canónico) el DFA y el
    oráculo coinciden."""
    alphabet = profile_alphabet(profile)
    n = 0
    for r in range(len(alphabet) + 1):
        for combo in combinations(alphabet, r):
            seq = list(combo)                       # ya está en orden canónico
            assert recognize(profile, seq) == profile_accepts(profile, seq), seq
            n += 1
    assert n == 2 ** len(alphabet)


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_is_dfa(profile):
    assert AUTOMATA[profile].is_deterministic()
    assert automaton_type(profile).startswith("DFA")


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_dfa_rejects_unordered_duplicate_and_foreign_tokens(profile):
    alphabet = profile_alphabet(profile)
    # un ejemplo aceptado (todos los tokens del alfabeto en orden)
    full = list(alphabet)
    assert recognize(profile, full)
    # duplicado
    assert not recognize(profile, full + [full[-1]])
    assert not recognize(profile, [full[0]] + full)
    # desordenado (invertido)
    assert not recognize(profile, list(reversed(full)))
    # token ajeno al perfil
    assert not recognize(profile, full + ["COBOL"])
    # vacío
    assert recognize(profile, []) == profile_accepts(profile, [])


def test_documento_full_stack():
    assert recognize("FULL_STACK_DEVELOPER",
                     ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"])


def test_documento_ml_engineer():
    seq = ["PYTHON", "PANDAS", "TENSORFLOW", "POSTGRESQL", "GIT"]
    assert recognize("MACHINE_LEARNING_ENGINEER", seq)
    assert accepted_profiles(seq) == ["MACHINE_LEARNING_ENGINEER"]


def test_full_stack_missing_required_slot_is_rejected():
    # falta backend
    assert not recognize("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT", "POSTGRESQL", "GIT"])
    # falta Git
    assert not recognize("FULL_STACK_DEVELOPER", ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL"])


def test_optional_slots_may_be_present_or_absent():
    base = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    with_api = ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "REST_API", "GIT"]
    assert recognize("FULL_STACK_DEVELOPER", base)
    assert recognize("FULL_STACK_DEVELOPER", with_api)


def test_multiple_options_in_one_slot():
    seq = ["JAVASCRIPT", "TYPESCRIPT", "REACT", "VUE", "NODE_JS", "MYSQL", "GIT"]
    assert recognize("FULL_STACK_DEVELOPER", seq)


def test_order_of_resume_does_not_matter_after_canonical_ordering():
    tokens = ["GIT", "POSTGRESQL", "NODE_JS", "REACT", "JAVASCRIPT"]
    res = classify_resume(tokens)
    assert res["FULL_STACK_DEVELOPER"]["result"] == "ACCEPTED"
    assert res["FULL_STACK_DEVELOPER"]["sequence"] == \
        ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]


def test_unordered_input_to_dfa_without_stage2_is_rejected():
    """Demuestra por qué existe el ordenamiento de la Etapa 2."""
    assert not recognize("FULL_STACK_DEVELOPER",
                         ["GIT", "POSTGRESQL", "NODE_JS", "REACT", "JAVASCRIPT"])


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_formal_definition_is_consistent(profile):
    fd = formal_definition(profile)
    assert set(fd) == {"Q", "Sigma", "delta", "q0", "F"}
    assert fd["q0"] in fd["Q"] and set(fd["F"]) <= set(fd["Q"])
    assert set(fd["Sigma"]) == set(profile_alphabet(profile))
    for (s, a), t in fd["delta"].items():
        assert s in fd["Q"] and t in fd["Q"] and a in fd["Sigma"]
    assert len(fd["Q"]) == len(profile_alphabet(profile)) + 1   # q_start + after_T


@pytest.mark.parametrize("profile", PROFILE_NAMES)
def test_explain_and_dot(profile, tmp_path):
    assert profile in explain_pattern(profile)
    out = tmp_path / "a.dot"
    export_dot(profile, str(out))
    assert out.read_text().startswith("digraph")
