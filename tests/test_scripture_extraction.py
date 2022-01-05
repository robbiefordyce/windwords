""" Unit test cases to ensure that the scriptures regex extracts the correct
    scripture references from provided text. 
"""
import pytest
from windwords.scriptures import Bible


def extract(text):
    """ 
    """
    bible = Bible()
    return [bible.reference_to_string(*ref) for ref in bible.extract(text)]


@pytest.fixture
def mark_8():
    return "Mark 8"

@pytest.fixture
def mark_8_34():
    return "Mark 8:34"

@pytest.fixture
def rev_2_20():
    return "Revelation of Jesus Christ 2:20"

@pytest.fixture
def wis_1_15():
    return "The Wisdom of Solomon 1:15"


def test_reference_lowercase(mark_8_34):
    assert mark_8_34 in extract("mark 8:34")

def test_reference_uppercase(mark_8_34):
    assert mark_8_34 in extract("MARK 8:34")

def test_reference_camelcase(mark_8_34):
    assert mark_8_34 in extract("Mark 8:34")

def test_multiword_reference_camelcase(rev_2_20):
    assert rev_2_20 in extract("reVElAtiOn oF JEsUS ChRIsT 2:20")

def test_apocryphal_multiword_reference_camelcase(wis_1_15):
    assert wis_1_15 in extract("THe wIsDOm oF SoLOmoN 1:15")

def test_reference_border_spaces(mark_8_34):
    assert mark_8_34 in extract(" mark 8:34  ")

def test_reference_border_text(mark_8_34):
    assert mark_8_34 in extract("hello mark 8:34  world")

# def test_reference_lowercase_no_colon(mark_8_34):
#     assert mark_8_34 in extract("mark 8 34")

# def test_reference_filler_words(mark_8_34):
#     assert mark_8_34 in extract("mark chapter 8 verse 34")

# def test_reference_filler_words_as_words(mark_8_34):
#     assert mark_8_34 in extract("mark chapter eight verse thirty four")

# def test_reference_lowercase_as_words(mark_8_34):
#     assert mark_8_34 in extract("mark eight thirty four")

def test_reference_chapter(mark_8):
    assert mark_8 in extract("mark 8")

# def test_reference_chapter_as_word(mark_8):
#     assert mark_8 in extract("mark eight")
