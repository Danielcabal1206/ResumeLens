"""Une las 4 etapas: regex → FST → autómatas → DSL textX → HTML/MD."""
from __future__ import annotations

from pathlib import Path

from textx import metamodel_from_file

from dsl.renderer import render_html, render_markdown
from dsl.validator import validate
from resumelens.contracts import CANONICAL, CATEGORY_TO_KEY
from resumelens.extraction.regex_extractor import extract, save as save_extracted
from resumelens.normalization.transducers import normalize_all
from resumelens.recognition.profile_automata import classify_resume

GRAMMAR = Path(__file__).resolve().parents[1] / "dsl" / "candidate_profile.tx"


def classify_profiles(tokens: list[str]) -> dict[str, dict]:
    return classify_resume(tokens)


def _quote(value: str) -> str:
    return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'


def to_dsl(extracted: dict, tokens: list[str], profiles: dict) -> str:
    groups: dict[str, list[str]] = {}
    for tok in tokens:
        key = CATEGORY_TO_KEY[CANONICAL[tok][0]]
        if tok not in groups.setdefault(key, []):
            groups[key].append(tok)

    lines = ["candidate {"]
    if extracted.get("name"):
        lines.append(f"    name : {_quote(extracted['name'][0])};")
    lines.append("    contact {")
    for kind in ("email", "phone", "linkedin", "github"):
        for value in extracted.get(kind, []):
            lines.append(f"        {kind} : {_quote(value)};")
    lines.append("    }")
    lines.append("    qualifications {")
    for kind, toks in groups.items():
        lines.append(f"        {kind} : [{', '.join(toks)}];")
    lines.append("    }")
    lines.append("    background {")
    for kind in ("education", "experience"):
        items = extracted.get(kind, [])
        if items:
            lines.append(f"        {kind} : [{', '.join(_quote(i) for i in items)}];")
    lines.append("    }")
    lines.append("    classification {")
    for profile, result in profiles.items():
        lines.append(f"        profile {profile} : {result['result']};")
    lines.append("    }")
    lines.append("}")
    return "\n".join(lines) + "\n"


def parse_and_render(dsl_text: str) -> tuple[object, str, str]:
    model = metamodel_from_file(str(GRAMMAR)).model_from_str(dsl_text)
    validate(model)
    return model, render_markdown(model), render_html(model)


def run_pipeline(text: str) -> dict:
    extracted = extract(text)
    tokens = normalize_all(extracted)
    profiles = classify_profiles(tokens)
    dsl_text = to_dsl(extracted, tokens, profiles)
    _model, markdown, html = parse_and_render(dsl_text)
    return {
        "extracted": extracted,
        "tokens": tokens,
        "profiles": profiles,
        "dsl": dsl_text,
        "markdown": markdown,
        "html": html,
    }


def write_outputs(result: dict, dest: Path, stem: str) -> dict[str, Path]:
    dest.mkdir(parents=True, exist_ok=True)
    paths = {
        "json": dest / f"{stem}.json",
        "dsl": dest / f"{stem}.rl",
        "md": dest / f"{stem}.md",
        "html": dest / f"{stem}.html",
    }
    save_extracted(result["extracted"], str(paths["json"]))
    paths["dsl"].write_text(result["dsl"], encoding="utf-8")
    paths["md"].write_text(result["markdown"], encoding="utf-8")
    paths["html"].write_text(result["html"], encoding="utf-8")
    return paths
