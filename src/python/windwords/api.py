""" `windwords` Application Programming Interface

    Provides high level entry points for interfacing with the underlying system
"""
from datetime import timedelta

from windwords import constants, mongo
from windwords.logging import LOGGER
from windwords.handlers import (
    ChurchHandler, YoutubeChannelHandler, YoutubeVideoHandler
)
from windwords.youtube import get_recent_videos_from_channel


def populate_sermons(delta=None):
    """ Runs through recent sermons from the available channels and adds
        acceptable video sermons into the Mongo database.

    Args:
        delta (datetime.timedelta): The preceeding period to resolve videos.
            Defaults to two weeks.
    """
    documents = [
        d for d in mongo.find_all(constants.Collection.CHANNELS.value)
        if d.get("channel_url")
    ]
    for document in documents:
        populate_sermons_from_channel(document.get("channel_url"), delta=delta)


def populate_sermons_from_channel(channel_url, delta=None):
    """ Runs through recent sermons from the specified channel and adds
        acceptable video sermons into the Mongo database.

    Args:
        channel_url (str): The url of the channel to consider videos from
        delta (datetime.timedelta): The preceeding period to resolve videos.
            Defaults to two weeks.
    """
    delta = delta or timedelta(weeks=2)
    channel = YoutubeChannelHandler.from_url(channel_url)
    for video in get_recent_videos_from_channel(channel_url, delta):
        LOGGER.info(f"{'-'*50}")
        LOGGER.info(f"{'-'*50}")
        LOGGER.info(f"Checking video: `{video.title}`")
        LOGGER.info(f"Video (URL): {video.watch_url}")
        LOGGER.info(f"Channel (URL): {channel_url}")
        if is_video_sermon(video.watch_url):
            insert_video_sermon(video.watch_url)
        else:
            LOGGER.info("Ignoring: Video is not sermon-compatible!")
         
            
def insert_channel_and_church(channel_url, church_gpid):
    """ Utility function for adding a channel and a church to the windwords
        database and ensuring that the two documents are linked.

    Args:
        channel_url (str): The url of the channel to be added.
        church_gpid (str): The Google Place ID of the church to be added.
    """
    channel = insert_channel(channel_url)
    church = insert_church(church_gpid)
    if not channel.is_linked(church):
        channel.link(church)
        LOGGER.info(
            f"LINKED channel `{channel.database_object_id()}` "
            f"to church `{church.database_object_id()}`"
        )
    if not church.is_linked(channel):
        church.link(channel)
        LOGGER.info(
            f"LINKED church `{church.database_object_id()}` "
            f"to channel `{channel.database_object_id()}`"
        )


def insert_channel(url):
    """ Adds the channel specified by url to the windwords Mongo database.
        No change will occur if the channel already exists. 

    Args:
        url (str): The url of the channel to be added.
    Returns:
        windwords.handlers.YoutubeChannelHandler: The channel handler.
    Raises:
        AssertionError: If the channel does not exist and could not be inserted
    """
    handler = YoutubeChannelHandler.from_url(url)
    if not handler.exists_in_database():
        object_id = handler.insert()
        LOGGER.info(f"INSERTED channel `{object_id}` from url `{url}`")
    return handler


def insert_church(gpid):
    """ Adds the church specified by the Google Place ID to the windwords Mongo
        database. No change will occur if the church already exists.

    Args:
        gpid (str): The Google Place ID of the church to be added.
    Returns:
        windwords.handlers.ChurchHandler: The church handler.
    Raises:
        AssertionError: If the church does not exist and could not be inserted
    """
    handler = ChurchHandler.from_google_place_id(gpid)
    if not handler.exists_in_database():
        object_id = handler.insert()
        LOGGER.info(f"INSERTED church `{object_id}` from Place ID `{gpid}`")
    return handler


def insert_video_sermon(url):
    """ Adds the video sermon specified by the url to the windwords Mongo
        database.

    Args:
        url (str): The url of the video sermon to be added.
    Returns:
        windwords.handlers.YoutubeVideoHandler: The sermon handler.
    Raises:
        AssertionError: 
            - If the sermon does not exist and could not be inserted
            - If an associated channel could be resolved but is not yet inserted
    """
    sermon = YoutubeVideoHandler.from_url(url)
    video = sermon.python_object
    # Ensure the video's channel exists
    channel = YoutubeChannelHandler.from_url(video.channel_url)
    assert channel.exists_in_database(), (
        f"Channel {video.channel_url} does not exist in database and should "
        "be inserted"
    )
    # Insert video into database
    if not sermon.exists_in_database():
        sermon.insert()
        LOGGER.info(
            f"INSERTED video sermon `{sermon.database_object_id()}` "
            f"from url `{url}`"
        )
    # Attempt to link to the channel
    sid = sermon.database_object_id()
    cid = channel.database_object_id()
    if not sermon.is_linked(channel):
        sermon.link(channel)
        LOGGER.info(f"LINKED video sermon `{sid}` to channel `{cid}`")
    if not channel.is_linked(sermon):
        channel.link(sermon)
        LOGGER.info(f"LINKED channel `{cid}` to video sermon `{sid}`")
    # Attempt to resolve a church and link to it
    church_id = (channel.get_linked_ids("church") or [None])[0]
    if church_id:
        church = ChurchHandler.from_object_id(church_id)
        assert church.exists_in_database(), (
            f"Church {church_id} does not exist in database and should be "
            "inserted"
        )
        if not sermon.is_linked(church):
            sermon.link(church)
            LOGGER.info(f"LINKED video sermon `{sid}` to church `{church_id}`")
        if not church.is_linked(sermon):
            church.link(sermon)
            LOGGER.info(f"LINKED church `{church_id}` to video sermon `{sid}`")
    return sermon


def is_video_sermon(url):
    """ Returns true if the given video url can be handled as a sermon.

        In order to constitute a "sermon", a given video must:
            > Have an associated channel
            > Have english captions
            > Contain at least one reference to biblical scripture

    Args:
        url (str): The url of the video to be assessed.
    Returns:
        bool: True if the video can be handled as a sermon.
    """
    sermon = YoutubeVideoHandler.from_url(url)
    video = sermon.python_object
    # Check whether:
    # 1) An associated channel exists
    # 2) Any english captions are available for the video
    if video.channel_url and any([c in video.captions for c in ("a.en", "en")]):
        # Return whether any scriptures were extracted from the video
        return bool(sermon.secondary_data().get("scriptures"))
    return False
