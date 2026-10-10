"""Validación semántica del modelo textX (lo que la gramática no puede expresar).

Reglas:
  1. Cada uno de los tokens existe en contracts.CANONICAL
  2. Cada uno de los tokens esta en el grupo que le corresponde, que vendria siendo CATEGORY_TO_KEY
  3. No hay grupos ni tokens repetidos
  4. Hay exactamente un resultado por cada perfil de contracts.PROFILES
  5. Cada veredicto coincide con el oraculo classify()
"""
from __future__ import annotations

from resumelens.contracts import CANONICAL, CATEGORY_TO_KEY, PROFILES, classify

class ProfileValidationError(Exception):
    def __init__(self, errors: list[str]):
        self.errors = list(errors)
        super().__init__("; ".join(self.errors))


def model_tokens(model) -> list[str]:
    return [t for g in model.groups for t in g.tokens]


def missing_slots(profile: str, tokens: list[str]) -> list[str]:
    present = set(tokens)
    return [name for name, opts, req in PROFILES[profile]
            if req and not present.intersection(opts)]


def validate(model) -> None:
    errors: list[str] = []
    tokens: list[str] = []
    seen_groups: set[str] = set()

    for g in model.groups:
        if g.kind in seen_groups:
            errors.append(f"group '{g.kind}' appears more than once")
        seen_groups.add(g.kind)
        for t in g.tokens:
            if t not in CANONICAL:
                errors.append(f"unknown token '{t}' in '{g.kind}'")
                continue
            expected = CATEGORY_TO_KEY[CANONICAL[t][0]]
            if expected != g.kind:
                errors.append(f"token '{t}' belongs in '{expected}', not '{g.kind}'")
            if t in tokens:
                errors.append(f"token '{t}' is repeated")
            tokens.append(t)

    declared: dict[str, bool] = {}
    for r in model.results:
        if r.profile not in PROFILES:
            errors.append(f"unknown profile '{r.profile}'")
        elif r.profile in declared:
            errors.append(f"profile '{r.profile}' is declared more than once")
        else:
            declared[r.profile] = (r.verdict == "ACCEPTED")
    for p in PROFILES:
        if p not in declared:
            errors.append(f"missing classification for profile '{p}'")

    if not errors:  # la coherencia solo tiene sentido con tokens y perfiles bien formados
        expected = classify(tokens)
        for p, accepted in declared.items():
            if accepted == expected[p]:
                continue
            if accepted:
                errors.append(f"{p} declared ACCEPTED but required slots are missing: "
                              f"{', '.join(missing_slots(p, tokens))}")
            else:
                errors.append(f"{p} declared REJECTED but the tokens satisfy the profile")

    if errors:
        raise ProfileValidationError(errors)


def matched_profiles(model) -> list[str]:
    return [r.profile for r in model.results if r.verdict == "ACCEPTED"]