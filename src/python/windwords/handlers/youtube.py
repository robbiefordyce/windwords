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
    def get_link_schema(cls):
        """ Returns a link schema that describes how this handler's document
            should link to the documents of other handlers.
            Link schema is a dictionary: {
                `handlerClassName`: {
                    "field": `str`,
                    "type": `windwords.constants.LinkType`
                }
            } 

        Returns:
            dict: The link schema for this handler.
        """
        return {
            "ChurchHandler": {
                "field": "church",
                "type": constants.LinkType.TO_ONE.value,
                #TODO: Update this TO_MANY later on, for sub-churches within an
                #organisation 
            },
            "YoutubeVideoHandler": {
                "field": "sermons",
                "type": constants.LinkType.TO_MANY.value,
            },
        }

    @classmethod
    def from_object_id(cls, object_id):
        """ Instantiates a YoutubeChannelHandler from a database object id. 

        Args:
            object_id (bson.ObjectId): A database object id.
        Returns:
            YoutubeChannelHandler: The handler.
        Raises:
            ValueError: If the specified object_id does not exist in the
                database. 
        """
        document = cls.get_document_from_object_id(object_id)
        if not document:
            raise ValueError(
                f"Could not find a document with id `{object_id}` in "
                f"collection `{cls.collection()}`"
            )
        return cls.from_url(document.get("channel_url"))

    @classmethod
    def from_url(cls, url):
        """ Instantiates a YoutubeChannelHandler from a url.
        
        Args:
            url (str): A Youtube channel url
        Returns:
            YoutubeChannelHandler: The handler.
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
            "srt": self.convert_srt_into_document(srt),
            "scriptures": self.extract_scriptures_from_srt(srt),
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
    def get_link_schema(cls):
        """ Returns a link schema that describes how this handler's document
            should link to the documents of other handlers.
            Link schema is a dictionary: {
                `handlerClassName`: {
                    "field": `str`,
                    "type": `windwords.constants.LinkType`
                }
            } 

        Returns:
            dict: The link schema for this handler.
        """
        return {
            "ChurchHandler": {
                "field": "church",
                "type": constants.LinkType.TO_ONE.value,
            },
            "YoutubeChannelHandler": {
                "field": "channel",
                "type": constants.LinkType.TO_ONE.value,
            },
        }

    @classmethod
    def from_object_id(cls, object_id):
        """ Instantiates a YoutubeChannelHandler from a database object id. 

        Args:
            object_id (bson.ObjectId): A database object id.
        Returns:
            YoutubeChannelHandler: The handler.
        Raises:
            ValueError: If the specified object_id does not exist in the
                database. 
        """
        document = cls.get_document_from_object_id(object_id)
        if not document:
            raise ValueError(
                f"Could not find a document with id `{object_id}` in "
                f"collection `{cls.collection()}`"
            )
        return cls.from_url(document.get("url"))

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
    def decompose_srt(srt):
        """ Given text in raw srt format, decomposes the file into its frames,
            timcodes and captions.

        Args:
            srt (str): Raw srt text
        Returns:
            Tuple(List[int], List[Tuple[str]], List[str]): A tuple of:
                - Frames (int)
                - Timecodes (tuple of (start, end) times)
                - Captions (str)
        """
        lines = srt.split("\n")
        frames = lines[::4]
        timecodes = lines[1::4]
        captions = lines[2::4]
        spaces = lines[3::4]
        # Asserts that every third line is an empty string
        # This indicates a split between this caption and the next!
        assert not any(spaces), "Unsupported srt structure provided!"
        # Do some processing to extract the start and end timecodes
        times = [t.split("-->") for t in timecodes]
        return (
            frames,
            [(start.strip(), end.strip()) for start, end in times],
            captions,
        )

    @staticmethod
    def convert_srt_into_document(srt):
        """ Converts raw srt text (as from a srt file) into a JSON document
            representation.

        Args:
            srt (str): Raw text from an srt file
        Returns:
            List[dict]: Srt data encoded into a JSON representation. 
        """
        output = []
        frames, timecodes, captions = YoutubeVideoHandler.decompose_srt(srt)
        for frame, times, caption in zip(frames, timecodes, captions):
            start, end = times
            output.append({
                "caption": caption,
                "frame": int(frame),
                "timecodes": {
                    "start": start,
                    "end": end,
                }
            })
        return output

    @staticmethod
    def extract_scriptures_from_srt(srt, allow_duplicates=False):
        """ Converts raw srt text (as from a srt file) into scripture
            references.

            When a “scripture reference” is returned, it is always a five value
            tuple consisting of:
            (‘Book name’, start chapter, start verse, end chapter, end verse)

        Args:
            srt (str): Raw text from an srt file
            allow_duplicates (bool): If true, no duplicate entries will be
                returned.
        Returns:
            List[scriptures.ScriptureReference]: Collection of extracted
                scripture references. 
        """
        _, _, captions = YoutubeVideoHandler.decompose_srt(srt)
        text = " ".join(captions)
        bible = Bible()
        references = [
            bible.reference_to_string(*ref) for ref in bible.extract(text)
        ]
        if not allow_duplicates:
            references = list(set(references))
        return sorted(references)

