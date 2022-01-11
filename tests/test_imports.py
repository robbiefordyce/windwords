""" Simple import unit test to ensure that required modules are available.
"""


def test_import_windwords():
    from windwords import api
    from windwords import constants
    from windwords import handlers
    from windwords import logging
    from windwords import mongo
    from windwords import scripture
    from windwords import words
    from windwords import youtube
