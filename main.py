"""Uso:  python main.py data/resumes/fullstack.txt"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from resumelens.pipeline import run_pipeline  # noqa: E402


def main(path: str) -> None:
    res = run_pipeline(Path(path).read_text(encoding="utf-8"))
    print("Candidato:", (res["extracted"]["name"] or ["?"])[0])
    print("Tokens canónicos:", ", ".join(res["tokens"]))
    for profile, r in res["profiles"].items():
        print(f"  {profile:28s} {r['result']:9s} {' '.join(r['sequence'])}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
