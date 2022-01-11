""" `windwords` Application Programming Interface

    Provides high level entry points for interfacing with the underlying system
"""
from datetime import timedelta

from windwords import constants, mongo
from windwords.logging import LOGGER
from windwords.handlers import YoutubeChannelHandler, YoutubeVideoHandler
from windwords.youtube import get_recent_videos_from_channel


def populate_sermons(delta=None):
    """ Runs through recent sermons from the available channels and adds
        acceptable video sermons into the Mongo database.

    Args:
        delta (datetime.timedelta): The preceeding period to resolve videos.
            Defaults to two weeks.
    """
    delta = delta or timedelta(weeks=2)
    channel_documents = mongo.find_all(constants.Collection.CHANNELS.value)
    for document in channel_documents:
        channel_url = document.get("channel_url")
        if not channel_url:
            LOGGER.warning(
                "Could not resolve `channel_url` for document "
                f"`{document.get('_id')}`"
            )
            continue
        for video in get_recent_videos_from_channel(channel_url, delta):
            LOGGER.info(f"{'-'*50}")
            LOGGER.info(f"Resolved video: `{video.title}`")
            LOGGER.info(f"  URL: {video.watch_url}")
            LOGGER.info(f"  Channel: {channel_url}")
            LOGGER.info(f"  Sermon: {is_video_sermon(video.watch_url)}")
            LOGGER.info(f"{'-'*50}")


def insert_channel(url):
    """ Adds the channel specified by url to the windwords Mongo database.
        If the channel already exists, the existing document will be returned. 

    Args:
        url (str): The url of the channel to be added.
    Returns:
        dict: The channel document.
    Raises:
        AssertionError: If the channel does not exist and could not be inserted
    """
    document = mongo.find_document(
        constants.Collection.CHANNELS.value,
        {"channel_url": url}
    )
    if document:
        LOGGER.debug(
            f"Resolved existing channel `{document.get('_id')}` "
            f"from url `{url}`"
        )
    else:
        handler = YoutubeChannelHandler.from_url(url)
        object_id = channel_handler.insert()
        document = mongo.find_document_by_id(
            constants.Collection.CHANNELS.value,
            object_id
        )
        assert document, f"Could not insert channel from url `{url}`"
        LOGGER.info(f"INSERTED channel `{object_id}` from url `{url}`")
    return document


def is_video_sermon(url):
    """ Returns true if the given video url can be handled as a sermon.

        In order to constitute a "sermon", a given video must:
            > Have english captions
            > Contain at least one reference to biblical scripture

    Args:
        url (str): The url of the video to be assessed.
    Returns:
        bool: True if the video can be handled as a sermon.
    """
    handler = YoutubeVideoHandler.from_url(url)
    video = handler.python_object
    # Check whether any english captions are available for the video
    if any([c in video.captions for c in ("a.en", "en")]):
        # Return whether any scriptures were extracted from the video
        return bool(handler.secondary_data().get("scriptures"))
    return False
