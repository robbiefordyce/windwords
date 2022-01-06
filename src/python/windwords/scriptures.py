import re

from scriptures.texts.kjv1611 import KingJames1611


class Bible(KingJames1611):
    def __init__(self):
        # Update books with commonly alternate names
        self.books.update(self.alternate_book_names())
        # Update book references with cardinal and ordinal numbers 
        self._update_book_numeral_regex()
        # Call the parent class to compile the regex with the updated book data
        super().__init__()
        # self.scripture_re = re.compile(
        #     r'\b(?P<BookTitle>%s)\s*'
        #     r'(?P<ChapterNumber>\d{1,3})'
        #     r'(?:\s*:\s*(?P<VerseNumber>\d{1,3}))?'
        #     r'(?:\s*[-\u2013\u2014]\s*'
        #     r'(?P<EndChapterNumber>\d{1,3}(?=\s*:\s*))?'
        #     r'(?:\s*:\s*)?'
        #     r'(?P<EndVerseNumber>\d{1,3})?'
        #     r')?' % (self.book_re_string,), re.IGNORECASE | re.UNICODE
        # )

    def alternate_book_names(self):
        """ Returns alternate biblical book names.
            (This supplements the base biblical dictionary)

            Some books in the bible are known by alternate names. Here we offer
            the regular expressions necessary to parse these against the
            standardised scripture reference.

        Returns:
            dict: A mapping of alternate bible book names. 
        """
        return {
            'song_alt1': (
                'Song of Solomon',
                'Song',
                'Song(?:s)?(?: of Son(?:gs)?)?',
                [17, 17, 11, 16, 16, 13, 13, 14]
            ),
            'song_alt2': (
                'Song of Solomon',
                'Song',
                'Cant(?:icle(?: of Cant(?:icles)?)?)?',
                [17, 17, 11, 16, 16, 13, 13, 14]
            ),
        }

    def _update_book_numeral_regex(self):
        """ Updates the internal book regex with cardinal and ordinal names.

        Example:
            `1 John` can also be referred to as:
            `I John`, `First John`, `One John`
        """
        for key, value in self.books.items():
            name, abbreviation, regex, verse_count = value
            for source, target in (
                ("(?:1|I)", "(?:1|I|1st|one|first)"),
                ("(?:2|II)", "(?:2|II|2nd|two|second)"),
                ("(?:3|III)", "(?:3|III|3rd|three|third)"),
            ):
                regex = regex.replace(source, target)
            self.books.update({key: (name, abbreviation, regex, verse_count)})
        