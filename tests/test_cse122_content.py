"""No model downloads or GPU required for the experiment content checks."""

import pytest

from samples.cse122_content import LESSONS, TEST_TEXTS, validate_splits


def sample_rows():
    return [
        {"id": "a", "split": "train", "text": "Câu một"},
        {"id": "b", "split": "eval", "text": "Câu hai"},
        {"id": "c", "split": "test", "text": "Câu ba"},
    ]


def test_content_has_six_aligned_slides_and_disjoint_test():
    assert len(LESSONS) == 6
    narration = {text for _, paragraphs in LESSONS for text in paragraphs}
    assert len(TEST_TEXTS) == 4
    assert not narration.intersection(TEST_TEXTS)
    assert all(len(text) < 400 for text in narration)


def test_accept_separate_splits():
    validate_splits(sample_rows())


@pytest.mark.parametrize("field,value", [("text", " CÂU   MỘT "), ("id", "a")])
def test_reject_leakage(field, value):
    rows = sample_rows()
    rows[2][field] = value
    with pytest.raises(ValueError, match="duplicate"):
        validate_splits(rows)


def test_missing_test_is_rejected():
    with pytest.raises(ValueError, match="Separate"):
        validate_splits(sample_rows()[:2])