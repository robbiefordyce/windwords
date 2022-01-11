"""
    A collection of constants pertaining to the windwords project.
"""
from enum import Enum
from pathlib import Path


# ----------- PATH CONSTANTS ----------
WINDWORDS_PYTHON = Path(__file__).parent.parent.absolute()
WINDWORDS_ROOT = WINDWORDS_PYTHON.parent.parent.absolute()
WINDWORDS_RESOURCES = WINDWORDS_ROOT.joinpath("resources")

# ----------- APPLICATION ----------
APPLICATION_NAME = "windwords"

# ----------- DATABASE ----------
DATABASE_NAME = "windwords_db"


class Collection(Enum):
    BOOKS = "books"
    CHANNELS = "channels"
    CHURCHES = "churches"
    SERMONS = "sermons"


class MediaFormat(Enum):
    AUDIO = "audio"
    VIDEO = "video"