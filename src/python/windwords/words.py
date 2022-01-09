import nltk
from nltk.corpus import stopwords


try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')


def get_stopwords():
    """ Returns english stopwords defined in NLTK.
        ("stopwords" are filler words, such as "in", "and" and "because"...)

    Returns:
        List[str]: A collection of stopwords.
    """
    return sorted(stopwords.words("english"))
    