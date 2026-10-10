import pytest

from resumelens.contracts import STAGE1_KEYS, classify
from resumelens.extraction.regex_extractor import extract
from resumelens.normalization.transducers import (
    normalize_all, normalize_term, order_for_profile,
)

CV_FULLSTACK = """Wednesday Addams
wednesday@mail.com | +57 300 123 4567
3 years of experience developing web applications.
Technical Skills:
JS, React.js, NodeJS, Postgres, Git
"""

CV_ML = """Mary Jane Watson
2 years of experience developing predictive models and data-processing pipelines.
Technical Skills:
Python, Pandas, NumPy, Scikit-learn, TensorFlow, SQL, Git
"""


def test_extract_has_all_keys():
    assert set(extract(CV_FULLSTACK)) == set(STAGE1_KEYS)


def test_extract_contact_and_experience():
    d = extract(CV_FULLSTACK)
    assert d["name"] == ["Wednesday Addams"]
    assert d["email"] == ["wednesday@mail.com"]
    assert d["experience"] == ["3 years of experience"]
    assert d["languages"] == ["JS"] and d["databases"] == ["Postgres"]


@pytest.mark.parametrize("text", ["we go to the rest of the team", "express thanks", "Go to market"])
def test_no_false_positives_on_common_words(text):
    d = extract(text)
    assert d["languages"] == [] and d["other_qualifications"] == [] and d["frameworks"] == []


def test_java_not_inside_javascript():
    assert extract("JavaScript")["languages"] == ["JavaScript"]


@pytest.mark.parametrize("raw,tok", [
    ("JS", "JAVASCRIPT"), ("Javascript", "JAVASCRIPT"), ("React.js", "REACT"), ("ReactJS", "REACT"),
    ("react", "REACT"), ("NodeJS", "NODE_JS"), ("Node.js", "NODE_JS"), ("Postgres", "POSTGRESQL"),
    ("sklearn", "SCIKIT_LEARN"), ("scikit learn", "SCIKIT_LEARN"), ("Scikit-learn", "SCIKIT_LEARN"),
    ("Tensor Flow", "TENSORFLOW"), ("Py Torch", "PYTORCH"), ("REST APIs", "REST_API"),
])
def test_normalize_term(raw, tok):
    assert normalize_term(raw) == tok


def test_unknown_term():
    assert normalize_term("COBOL") is None


def test_every_variant_roundtrips():
    from resumelens.contracts import VARIANT_TO_TOKEN
    for v, tok in VARIANT_TO_TOKEN.items():
        assert normalize_term(v) == tok


def test_canonical_order_independent_of_input_order():
    a = order_for_profile(["GIT", "NODE_JS", "JAVASCRIPT", "POSTGRESQL", "REACT"], "FULL_STACK_DEVELOPER")
    assert a == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]


def test_pipeline_fullstack():
    toks = normalize_all(extract(CV_FULLSTACK))
    assert toks == ["JAVASCRIPT", "REACT", "NODE_JS", "POSTGRESQL", "GIT"]
    res = classify(toks)
    assert res["FULL_STACK_DEVELOPER"] and not res["MACHINE_LEARNING_ENGINEER"]


def test_pipeline_ml():
    toks = normalize_all(extract(CV_ML))
    assert classify(toks)["MACHINE_LEARNING_ENGINEER"]
    assert not classify(toks)["FULL_STACK_DEVELOPER"]
