#Im too dumb to program on HTML so the agent helped me with this one. Made by Szztur's Agent lol


from __future__ import annotations

from html import escape

from dsl.validator import matched_profiles

NOTE = ("This report only checks whether the explicit qualifications match a formal "
        "pattern. It does not rank candidates or make hiring decisions.")

def _pretty(profile: str) -> str:
    return profile.replace("_", " ").title()


def _sections(model) -> dict:
    """Datos comunes a Markdown y HTML."""
    return {
        "name": model.name or "Unnamed candidate",
        "contact": [(c.kind, c.value) for c in model.contacts],
        "qualifications": [(g.kind, list(g.tokens)) for g in model.groups],
        "background": [(b.kind, list(b.items)) for b in model.background],
        "results": [(r.profile, r.verdict) for r in model.results],
        "matched": matched_profiles(model),
    }


def render_markdown(model) -> str:
    s = _sections(model)
    out = [f"# Candidate: {s['name']}", ""]
    out += ["## Contact", ""] + ([f"- **{k}**: {v}" for k, v in s["contact"]] or ["- (none found)"]) + [""]
    out += ["## Qualifications", ""]
    out += [f"- **{k}**: {', '.join(t)}" for k, t in s["qualifications"]] or ["- (none found)"]
    out += ["", "## Background", ""]
    out += [f"- **{k}**: {'; '.join(i)}" for k, i in s["background"]] or ["- (none found)"]
    out += ["", "## Profile match", "", "| Profile | Result |", "|---|---|"]
    out += [f"| {_pretty(p)} | {v} |" for p, v in s["results"]]
    matched = ", ".join(_pretty(p) for p in s["matched"]) or "none"
    out += ["", f"**Matched profiles:** {matched}", "", f"> {NOTE}", ""]
    return "\n".join(out)


def render_html(model) -> str:
    s = _sections(model)
    e = escape

    def ul(items: list[str]) -> str:
        body = "".join(f"<li>{i}</li>" for i in items) or "<li>(none found)</li>"
        return f"<ul>{body}</ul>"

    rows = "".join(
        f"<tr><td>{e(_pretty(p))}</td><td class=\"{v.lower()}\">{v}</td></tr>"
        for p, v in s["results"])
    matched = e(", ".join(_pretty(p) for p in s["matched"]) or "none")
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>ResumeLens - {e(s['name'])}</title>
<style>
body {{ font-family: sans-serif; max-width: 42rem; margin: 2rem auto; color: #111; background: #fff; }}
table {{ border-collapse: collapse; }}
td, th {{ border: 1px solid #999; padding: .3rem .8rem; }}
.accepted {{ color: #0a7a2f; font-weight: bold; }}
.rejected {{ color: #a33; }}
</style>
</head>
<body>
<h1>Candidate: {e(s['name'])}</h1>
<h2>Contact</h2>
{ul([f"<b>{e(k)}</b>: {e(v)}" for k, v in s['contact']])}
<h2>Qualifications</h2>
{ul([f"<b>{e(k)}</b>: {e(', '.join(t))}" for k, t in s['qualifications']])}
<h2>Background</h2>
{ul([f"<b>{e(k)}</b>: {e('; '.join(i))}" for k, i in s['background']])}
<h2>Profile match</h2>
<table><tr><th>Profile</th><th>Result</th></tr>{rows}</table>
<p><b>Matched profiles:</b> {matched}</p>
<p><em>{e(NOTE)}</em></p>
</body>
</html>
"""