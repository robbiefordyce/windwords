import re

from num2words import num2words
from words2num import words2num
from scriptures.texts.kjv1611 import KingJames1611

from windwords.words import get_stopwords


class Bible(KingJames1611):

    _CHAPTER_WORDS = ["chapter", "chapters"]
    _VERSE_WORDS = ["verse", "verses"]

    def __init__(self):
        # Update books with commonly alternate names
        self.books.update(self.alternate_book_names())
        # Update book references with cardinal and ordinal numbers 
        self._update_book_numeral_regex()
        # Call the parent class to compile the regex with the updated book data
        super().__init__()
        self.scripture_re = re.compile(
            self.get_scripture_regex(), re.IGNORECASE | re.UNICODE
        )

    @property
    def total_book_count(self):
        return len(self.books)

    @property
    def maximum_chapter_count(self):
        return max([
            len(verse_counts) for _,_,_,verse_counts in self.books.values()
        ])

    @property
    def maximum_verse_count(self):
        return max([
            count for _,_,_,verse_counts in self.books.values()
            for count in verse_counts
        ])

    def get_scripture_regex(self):
        """ Returns the regular expression for extracting scripture references
            from arbitrary text.

        Returns:
            str: The scripture regular expression.
        """
        sw =  get_stopwords() # generic stop words
        # Build regex
        chapter_re = self._words_to_regex(self._CHAPTER_WORDS + sw)
        verse_re = self._words_to_regex(self._VERSE_WORDS + sw)
        
        return (
            fr'\b(?P<BookTitle>{self.book_re_string})\s*'
            fr'(?:{chapter_re}|\s)*'
            r'(?P<ChapterNumber>\d{1,3})'
            fr'(?:{verse_re}|\s)*'
            r'(?:\s*:*\s*(?P<VerseNumber>\d{1,3}))?'
            fr'(?:{chapter_re}|\s)*'
            r'(?:\s*[-\u2013\u2014]*\s*'
            r'(?P<EndChapterNumber>\d{1,3}(?=\s*:\s*))?'
            fr'(?:{verse_re}|\s)*'
            r'(?:\s*:\s*)?'
            r'(?P<EndVerseNumber>\d{1,3})?'
            r')?'
        )

    def extract(self, text):
        """ Extract a list of tupled scripture references from a block of text.

        Args:
            text (str): Given text
        Returns:
            List[Tuple]: Matched scripture references
        """
        # convert all number words to digits 
        for word in re.findall(self.words_to_numbers_regex(), text):
            text = text.replace(word, str(words2num(word)))
        return super().extract(text)

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

    def _words_to_regex(self, words):
        """ Utility to convert a list of words into a bitwise OR regular
            expression. 
            i.e. ab|cd - match ab OR cd

        Args:
            words (List[str]): A collection of words
        Returns:
            str: A regular expression.
        """
        return "|".join(sorted(words, key=lambda s: len(s), reverse=True))
        
    def words_to_numbers_regex(self):
        """ Regular expression for returning a bitwise OR list of numbers as
            words.

            The expression only goes up to the maximum biblical verse count
            (nothing further than this is required for extracting scripture
            references)

        Returns:
            str: A regular expression.
        """
        max_number = max(self.maximum_chapter_count, self.maximum_verse_count)
        words = [
            num2words(n).replace("-", " ") for n in range(1, max_number+1)
        ]
        return self._words_to_regex(words)
