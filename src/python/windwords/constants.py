"""
    A collection of constants pertaining to the windwords project.
"""
from enum import Enum


class Database(Enum):
    DEFAULT_NAME = "windwords_db"


class Collection(Enum):
    BOOKS = "books"
    CHANNELS = "channels"
    CHURCHES = "churches"
    DENOMINATIONS = "denominations"
    SERMONS = "sermons"


class MediaFormat(Enum):
    AUDIO = "audio"
    VIDEO = "video"