import json
from cachetools import cached

from windwords.constants import WINDWORDS_RESOURCES


@cached(cache={})
def get_json_resource(filename):
    """ Returns english stopwords defined in NLTK.
        ("stopwords" are filler words, such as "in", "and" and "because"...)

    Returns:
        List[str]: A collection of stopwords.
    """
    filename = filename if filename.endswith(".json") else filename + ".json"
    path = WINDWORDS_RESOURCES.joinpath(filename)
    with open(path, "r") as infile:
        return json.load(infile)


def get_biblical_books():
    """ Returns the biblical books.

    Returns:
        List[dict]: A collection of biblical books.
    """
    return get_json_resource("bible.json")


def get_stopwords():
    """ Returns english stopwords defined in NLTK.
        ("stopwords" are filler words, such as "in", "and" and "because"...)

    Returns:
        List[str]: A collection of stopwords.
    """
    return get_json_resource("stopwords.json")
