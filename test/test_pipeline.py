from pathlib import Path

import pytest

from resumelens.pipeline import run_pipeline

RESUMES = Path(__file__).resolve().parents[1] / "data" / "resumes"

EXPECTED = {
    "fullstack.txt": ["FULL_STACK_DEVELOPER"],
    "ml_engineer.txt": ["MACHINE_LEARNING_ENGINEER"],
    "backend.txt": ["BACKEND_DEVELOPER"],
    "data_analyst.txt": ["DATA_ANALYST"],
    "incomplete.txt": [],
}


@pytest.mark.parametrize("filename,expected", EXPECTED.items())
def test_sample_resumes(filename, expected):
    res = run_pipeline((RESUMES / filename).read_text(encoding="utf-8"))
    accepted = [p for p, r in res["profiles"].items() if r["result"] == "ACCEPTED"]
    assert accepted == expected


def test_document_example_sequences():
    res = run_pipeline((RESUMES / "fullstack.txt").read_text(encoding="utf-8"))
    assert res["profiles"]["FULL_STACK_DEVELOPER"]["sequence"] == \
        ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
