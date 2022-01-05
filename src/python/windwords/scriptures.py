import re

from scriptures.texts.kjv1611 import KingJames1611


class Bible(KingJames1611):
    def __init__(self):
        super().__init__()
        # self.scripture_re = re.compile(
        #     r'\b(?P<BookTitle>%s)\s*'
        #      '(?P<ChapterNumber>\d{1,3})'
        #      '(?:\s*:\s*(?P<VerseNumber>\d{1,3}))?'
        #      '(?:\s*[-\u2013\u2014]\s*'
        #      '(?P<EndChapterNumber>\d{1,3}(?=\s*:\s*))?'
        #      '(?:\s*:\s*)?'
        #      '(?P<EndVerseNumber>\d{1,3})?'
        #      ')?' % (self.book_re_string,), re.IGNORECASE | re.UNICODE
        # )