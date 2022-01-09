""" Unit test cases to ensure that the scriptures regex extracts the correct
    scripture references from provided text. 
"""
import pytest
from windwords.scripture import Bible


def extract(text):
    """ Extract a stringified scripture reference from incoming text.
    
    Args:
        text (str): Any incoming text representing a scripture reference.
    Returns:
        str: The parsed scripture reference.
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
def second_timothy_3_16():
    return "II Timothy 3:16"

@pytest.fixture
def exodus_2_3to5():
    return "Exodus 2:3-5"

@pytest.fixture
def john_1_2to_3_4():
    return "John 1:2-3:4"

@pytest.fixture
def rev_2_20():
    return "Revelation of Jesus Christ 2:20"

@pytest.fixture
def wis_1_15():
    return "The Wisdom of Solomon 1:15"

@pytest.fixture
def sol_1_2():
    return "Song of Solomon 1:2"


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

def test_reference_chapter(mark_8):
    assert mark_8 in extract("mark 8")

def test_reference_border_spaces(mark_8_34):
    assert mark_8_34 in extract(" mark 8:34  ")

def test_reference_border_text(mark_8_34):
    assert mark_8_34 in extract("hello mark 8:34  world")

def test_reference_leading_digit(second_timothy_3_16):
    assert second_timothy_3_16 in extract("2 timothy 3:16")

def test_reference_leading_digit_as_roman_numeral(second_timothy_3_16):
    assert second_timothy_3_16 in extract("II timothy 3:16")

def test_reference_leading_digit_as_cardinal_word(second_timothy_3_16):
    assert second_timothy_3_16 in extract("two timothy 3:16")

def test_reference_leading_digit_as_ordinal_word(second_timothy_3_16):
    assert second_timothy_3_16 in extract("second timothy 3:16")

def test_reference_leading_digit_as_ordinal_number(second_timothy_3_16):
    assert second_timothy_3_16 in extract("2nd timothy 3:16")

# def test_reference_lowercase_no_colon(mark_8_34):
#     assert mark_8_34 in extract("mark 8 34")

def test_reference_leading_digit_as_roman_numeral(second_timothy_3_16):
    assert second_timothy_3_16 in extract("II timothy 3:16")

def test_reference_leading_digit_as_cardinal_word(second_timothy_3_16):
    assert second_timothy_3_16 in extract("two timothy 3:16")

def test_reference_leading_digit_as_ordinal_word(second_timothy_3_16):
    assert second_timothy_3_16 in extract("second timothy 3:16")

def test_reference_leading_digit_as_ordinal_number(second_timothy_3_16):
    assert second_timothy_3_16 in extract("2nd timothy 3:16")

def test_reference_lowercase_no_colon(mark_8_34):
    assert mark_8_34 in extract("mark 8 34")

def test_reference_filler_words(mark_8_34):
    assert mark_8_34 in extract("go to mark in chapter 8 and verse 34")

# def test_reference_lowercase_as_words(mark_8_34):
#     assert mark_8_34 in extract("mark eight thirty four")

def test_reference_multi_verse(exodus_2_3to5):
    assert exodus_2_3to5 in extract("exodus 2:3-5")

def test_reference_multi_verse_hyphen_only(exodus_2_3to5):
    assert exodus_2_3to5 in extract("exodus 2 3-5")

def test_reference_multi_verse_spaces(exodus_2_3to5):
    assert exodus_2_3to5 in extract("exodus 2 3 5")

def test_reference_multi_verse_filler_words(exodus_2_3to5):
    assert exodus_2_3to5 in extract("exodus chapter 2 verses 3 through to 5")

def test_reference_multi_chapter(john_1_2to_3_4):
    assert john_1_2to_3_4 in extract("john 1:2-3:4")

def test_reference_multi_chapter_spaced(john_1_2to_3_4):
    assert john_1_2to_3_4 in extract("john 1:2 3:4")

def test_reference_multi_chapter_filler_words(john_1_2to_3_4):
    assert john_1_2to_3_4 in extract(
        "john chapter 1 verse 2 through to chapter 3 verse 4"
    )

# def test_reference_filler_words_as_words(mark_8_34):
#     assert mark_8_34 in extract("mark chapter eight verse thirty four")

# def test_reference_chapter_as_word(mark_8):
#     assert mark_8 in extract("mark eight")

def test_reference_multiple(rev_2_20, exodus_2_3to5):
    verses = extract((
        "today we will be looking at revelation chapter 2 verse 20 and also "
        "exodus chapter 2 verses 3 through to 5"
    ))
    assert rev_2_20 in verses
    assert exodus_2_3to5 in verses

def test_reference_alternate_book_name(sol_1_2):
    assert sol_1_2 in extract("Songs 1:2")
    assert sol_1_2 in extract("Song of Son 1:2")
    assert sol_1_2 in extract("Song of Sol 1:2")
    assert sol_1_2 in extract("Song of Solomon 1:2")
    assert sol_1_2 in extract("Song of Songs 1:2")
    assert sol_1_2 in extract("Cant of Cant 1:2")
    assert sol_1_2 in extract("Canticle of Canticles 1:2")
