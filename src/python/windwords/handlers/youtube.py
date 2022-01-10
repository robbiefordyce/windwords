from pytube import Channel, YouTube
from urllib.parse import urlparse

from windwords import constants
from windwords.youtube import download_captions
from windwords.scripture import Bible
from windwords.handlers.base import DocumentHandler


class YoutubeChannelHandler(DocumentHandler):
    
    def primary_data(self):
        """ Resolves the primary fields and values.
            Primary fields are used for database lookups and therefore should
            not consist of complex objects.

        Returns:
            dict: The primary fields and associated values.
        """
        channel = self.python_object
        return {
            "channel_id": channel.channel_id,
            "channel_url": channel.channel_url,
            "host": urlparse(channel.channel_url).hostname,
            "name": channel.channel_name, 
        }

    @classmethod
    def accepts(cls, obj):
        """ Returns true if this handler can accept the specified object.

        Args:
            (obj, object): Any provided python object.
        Returns:
            bool: True if the handler can handle the provided object.
        """
        return isinstance(obj, Channel)

    @classmethod
    def collection(cls):
        """ Returns the database collection name associated with this handler.
            This property must be overridden by subclasses.

        Returns:
            (str): The collection name.
        """
        return constants.Collection.CHANNELS.value

    @classmethod
    def from_url(cls, url):
        """ Instantiates a YoutubeChannelHandler from a url.
        
        Args:
            (url, str): A Youtube channel url
        Returns:
            (YoutubeChannelHandler): The handler.
        """
        return cls(Channel(url))


class YoutubeVideoHandler(DocumentHandler):

    def primary_data(self):
        """ Resolves the primary fields and values.
            Primary fields are used for database lookups and therefore should
            not consist of complex objects.

        Returns:
            dict: The primary fields and associated values.
        """
        video = self.python_object
        return {
            "author": video.author,
            "captions": [caption.name for caption in video.captions],
            "description": video.description,
            "duration": video.length,
            "host": urlparse(video.watch_url).hostname,
            "media_format": constants.MediaFormat.VIDEO.value,
            "publish_date": video.publish_date,
            "thumbnail_url": video.thumbnail_url,
            "title": video.title,
            "url": video.watch_url,
            "video_id": video.video_id,
        }

    def secondary_data(self):
        """ Resolves the secondary fields and values.
            Secondary fields are not necessary to uniquely identify a document.
            Secondary fields may have a greater computation complexity and are
            only intended to be computed prior to insertion.

        Returns:
            dict: The secondary fields and associated values.
        """
        video = self.python_object
        srt = download_captions(video.watch_url)
        return {
            "srt": self.convert_srt_text_into_document(srt),
            "scriptures": self.convert_srt_text_into_scriptures(srt),
        }

    @classmethod
    def accepts(cls, obj):
        """ Returns true if this handler can accept the specified object.

        Args:
            (obj, object): Any provided python object.
        Returns:
            bool: True if the handler can handle the provided object.
        """
        return isinstance(obj, YouTube)

    @classmethod
    def collection(cls):
        """ Returns the database collection name associated with this handler.
            This property must be overridden by subclasses.

        Returns:
            (str): The collection name.
        """
        return constants.Collection.SERMONS.value

    @classmethod
    def from_url(cls, url):
        """ Instantiates a YoutubeVideoHandler from a url.
        
        Args:
            (url, str): A Youtube video url
        Returns:
            (YoutubeVideoHandler): The handler.
        """
        return cls(YouTube(url))

    @staticmethod
    def convert_srt_text_into_document(text):
        """ Converts raw srt text (as from a srt file) into a JSON document
            representation.

        Args:
            text (str): Raw text from an srt file
        Returns:
            List[dict]: Srt data encoded into a JSON representation. 
        """
        output = []
        lines = text.split("\n")
        frames = lines[::4]
        timecodes = lines[1::4]
        captions = lines[2::4]
        spaces = lines[3::4]
        # Asserts that every third line is an empty string
        # This indicates a split between this caption and the next!
        assert not any(spaces), "Unsupported srt structure provided!"
        for frame, times, caption in zip(frames, timecodes, captions):
            start, end = times.split("-->")
            output.append({
                "caption": caption,
                "frame": int(frame),
                "timecodes": {
                    "start": start.strip(),
                    "end": end.strip(),
                }
            })
        return output

    @staticmethod
    def convert_srt_text_into_scriptures(text, allow_duplicates=False):
        """ Converts raw srt text (as from a srt file) into scripture
            references.

            When a “scripture reference” is returned, it is always a five value
            tuple consisting of:
            (‘Book name’, start chapter, start verse, end chapter, end verse)

        Args:
            text (str): Raw text from an srt file
            allow_duplicates (bool): If true, no duplicate entries will be
                returned.
        Returns:
            List[scriptures.ScriptureReference]: Collection of extracted
                scripture references. 
        """
        bible = Bible()
        references = [
            bible.reference_to_string(*ref) for ref in bible.extract(text)
        ]
        if not allow_duplicates:
            references = list(set(references))
        return sorted(references)

