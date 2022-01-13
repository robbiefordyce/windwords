import os
import time
import googlemaps
from cachetools import cached


__CLIENT = None # The Google Maps API client


def get_client():
    """ Connects to Google Maps APIs.

    Returns:
        googlemaps.Client: The Google Maps client.
    """
    global __CLIENT
    if not __CLIENT:
        __CLIENT = connect_to_google_places_client()
    return __CLIENT


def connect_to_google_places_client(api_key=None):
    """ Connects to Google Maps API.

    Args:
        api_key (str, optional): The Google Maps API Key of the connecting
            user. Defaults to the `GOOGLE_MAPS_API_KEY` environment variable. 
    Returns:
        googlemaps.Client: The Google Maps API client.
    """
    api_key = api_key or os.getenv("GOOGLE_MAPS_API_KEY")
    return googlemaps.Client(key=api_key)


@cached(cache={})
def get_place(place_id):
    """ Returns a Google Place from the given google place id.

    Args:
        place_id (str): A Google Place Id.
    Returns:
        dict: Serialized Google Place data. 
    """
    return get_client().place(place_id)


def get_places_by_query(query, query_type="textquery"):
    """ Yields Google Place results from the given text input query.
        
    Args:
        query (str): The text input specifying which place to search for (for
            example, a name, address, or phone number).
        query_type (str): The type of input. This can be one of either
            'textquery' or 'phonenumber'. Defaults to 'textquery'.
    Yields:
        dict: Serialized Google Place data matching the query.
    """
    for result in get_place_ids_by_query(query, query_type=query_type):
        yield get_place(result)


@cached(cache={})
def get_place_ids_by_query(query, query_type="textquery"):
    """ Returns Google Place IDs from the given text input query.
        
    Args:
        query (str): The text input specifying which place to search for (for
            example, a name, address, or phone number).
        query_type (str): The type of input. This can be one of either
            'textquery' or 'phonenumber'. Defaults to 'textquery'.
    Returns:
        List[str]: Serialized Google Place ids matching the query.
    """
    results = get_client().find_place(query, query_type).get("candidates", [])
    return [r.get("place_id") for r in results if r.get("place_id")]


@cached(cache={})
def get_places_by_type(
        place_type,
        location=None,
        radius=None,
        region=None,
        query=None,
        next_page_token=None,
    ):
    """ Returns Google Places from the given Google place type.

    Args:
        place_type (str): Restricts the results to places matching the
            specified type.The full list of supported types is available here:
            https://developers.google.com/places/supported_types
        location (Optional[Tuple[str]]): The latitude/longitude value for which
            you wish to obtain the closest, human-readable address.
        radius (Optional[int]): Distance in meters within which to bias results
        region (Optional[str]): The region code, for example "NZ". See more @:
            https://developers.google.com/places/web-service/search
        query (Optional[str]): The text string on which to search
        next_page_token (Optional[str]): Token from a previous search that when
            provided will return the next page of results for the same search.
    Returns:
        dict: Serialized Google Place data. 
    """
    return get_client().places(
        query=query,
        location=location,
        radius=radius,
        type=place_type,
        region=region,
        page_token=next_page_token,
    )


@cached(cache={})
def get_all_places_by_type(
        place_type, location=None, radius=None, region=None, query=None,
    ):
    """ Returns the maximum number of Google Places from the given Google
        place type.

    Args:
        place_type (str): Restricts the results to places matching the
            specified type.The full list of supported types is available here:
            https://developers.google.com/places/supported_types
        location (Optional[Tuple[str]]): The latitude/longitude value for which
            you wish to obtain the closest, human-readable address.
        radius (Optional[int]): Distance in meters within which to bias results
        region (Optional[str]): The region code, for example "NZ". See more @:
            https://developers.google.com/places/web-service/search
        query (Optional[str]): The text string on which to search
    Returns:
        List[dict]: Serialized Google Place data. 
    """
    return _poll_all_results(
        get_places_by_type,
        place_type,
        location=location,
        radius=radius,
        region=region,
        query=query,
    )


@cached(cache={})
def geocode(address):
    """ Attempt to resolve a Place from an address.

    Args:
        address (str): the address text
    Returns:
        List[dict]: Google Place results matching the resolved address
    """
    return get_client().geocode(address)


@cached(cache={})
def reverse_geocode(latitude, longitude):
    """ Attempt to resolve a Place from latitude and longitude coordinates.

    Args:
        latitude (float): the latitude coordinate
        longitude (float): the longitude coordinate
    Returns:
        List[dict]: Google Place results matching the resolved address
    """
    return get_client().reverse_geocode((latitude, longitude))


def _poll_all_results(fn, *args, **kwargs):
    """ Iterates through Google Maps results until the maximum results are
        returned (caps at 60 results).

    Args:
        fn (function): A function (should return a JSON dictionary with
            "results" and "next_page_token" keys)
        args (args): function arguments
        kwargs (kwargs): function keyword arguments
    Returns:
        List[dict]: A list of JSON results
    """
    results = []
    next_page_token = True
    while(next_page_token):
        result = fn(*args, **kwargs) or {}
        results.extend(result.get("results", []))
        next_page_token = result.get("next_page_token", None)
        kwargs.update({"next_page_token": next_page_token})
        # From Google Docs: https://developers.google.com/maps/documentation/places/web-service/search-text
        # "There is a short delay between when a next_page_token is issued,
        # and when it will become valid."
        time.sleep(2)
    return results
