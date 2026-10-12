"""Uso:  python main.py data/resumes/fullstack.txt"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "src"))

from src.resumelens.pipeline import run_pipeline, write_outputs  # noqa: E402


def main(path: str) -> None:
    src = Path(path)
    res = run_pipeline(src.read_text(encoding="utf-8"))
    out_dir = ROOT / "output"
    paths = write_outputs(res, out_dir, src.stem)
    print("Candidato:", (res["extracted"]["name"] or ["?"])[0])
    print("Tokens canónicos:", ", ".join(res["tokens"]))
    for profile, r in res["profiles"].items():
        print(f"  {profile:28s} {r['result']:9s} {' '.join(r['sequence'])}")
    print("Salida:")
    for kind, p in paths.items():
        print(f"  {kind:4s} {p}")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    main(sys.argv[1])
