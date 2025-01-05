import pytest
from src.tools.pii_purifier import PIIPurifier


@pytest.fixture
def purifier():
    return PIIPurifier()


def test_purify(purifier):
    text = (
        "This is a test text with some PII like John Doe,"
        " 555-555-5555, and test@mail.com"
    )
    purify_text = purifier.purify(text)
    assert purify_text == text
