from pytube import Channel, YouTube


def get_videos_from_channel(url):
    """ Yields all videos associated with the given YouTube channel url.

    Args:
        url (str): A YouTube channel url.
    Yields:
        (pytube.Youtube): Youtube video instances.
    """
    channel = Channel(url)
    for video in channel.videos_generator():
        yield video


def get_videos_from_channel_within_timeframe(url, start_date, end_date):
    """ Yields videos associated with the given YouTube channel url within the
        specified time frame.

    Args:
        url (str): A YouTube channel url.
        start_date (datetime.datetime): The start date.
        end_date (datetime.datetime): The end date.
    Yields:
        (pytube.Youtube): Youtube video instances.
    """
    for video in get_videos_from_channel(url):  
        date = video.publish_date
        if date >= start_date and date <= end_date:
            yield video


def get_recent_videos_from_channel(url, delta):
    """ Yields recent videos associated with the given YouTube channel url.

    Args:
        url (str): A YouTube channel url.
        delta (datetime.timedelta): The preceeding period to resolve videos.
    Yields:
        (pytube.Youtube): Youtube video instances.
    """
    now = datetime.now()
    for video in get_videos_from_channel_within_timeframe(url, now-delta, now):
        yield video


def download_captions(url, language_codes=None):
    """ Downloads the captions from a youtube video and returns these in srt
        format.
    
    Args:
        url (str): A valid youtube URL.
        language_code (tuple(str)): The language of the captions to extract.
            Defaults to ('a.en', 'en') - autogenerated English, English. 
    Returns:
        Optional[str]: Captions encoded in srt format.
    """
    language_codes = language_codes or ("a.en", "en")
    video = YouTube(url)
    for code in language_codes:
        caption = video.captions.get(code)
        if caption:
            return caption.generate_srt_captions()
    return None


"""
Nasty hack:
    Because of the bug reported here in pytube-11.0.2:
    https://stackoverflow.com/questions/68780808/xml-to-srt-conversion-not-working-after-installing-pytube
    We are patching the xml_caption_to_srt function with the following 'fix'...

    TODO: Remove when pytube fixes this bug.
"""

import xml.etree.ElementTree as ElementTree
from html import unescape
from pytube import Caption


def xml_caption_to_srt(self, xml_captions: str) -> str:
    """Convert xml caption tracks to "SubRip Subtitle (srt)".

    :param str xml_captions:
        XML formatted caption tracks.
    """
    segments = []
    root = ElementTree.fromstring(xml_captions)
    for i, child in enumerate(list(root.findall('body/p'))):
        text = ''.join(child.itertext()).strip()
        if not text:
            continue
        caption = unescape(text.replace("\n", " ").replace("  ", " "),)
        try:
            duration = float(child.attrib["d"])
        except KeyError:
            duration = 0.0
        start = float(child.attrib["t"])
        end = start + duration
        sequence_number = i + 1  # convert from 0-indexed to 1.
        line = "{seq}\n{start} --> {end}\n{text}\n".format(
            seq=sequence_number,
            start=self.float_to_srt_time_format(start),
            end=self.float_to_srt_time_format(end),
            text=caption,
        )
        segments.append(line)
    return "\n".join(segments).strip()

Caption.xml_caption_to_srt = xml_caption_to_srt
