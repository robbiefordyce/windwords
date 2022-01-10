import json
from cachetools import cached

from windwords.constants import WINDWORDS_RESOURCES


@cached(cache={})
def get_stopwords():
    """ Returns english stopwords defined in NLTK.
        ("stopwords" are filler words, such as "in", "and" and "because"...)

    Returns:
        List[str]: A collection of stopwords.
    """
    path = WINDWORDS_RESOURCES.joinpath("stopwords.json")
    with open(path, "r") as infile:
        return json.load(infile)
