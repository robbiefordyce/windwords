import re
import requests
from collections import Counter
from bs4 import BeautifulSoup

from windwords import constants, google
from windwords.logging import LOGGER
from windwords.handlers.base import DocumentHandler


class ChurchHandler(DocumentHandler):

    # Attributes necessary to instantiate
    _REQUIRED_ATTRIBUTES = [
        "country",
        "gpid",
        "latitude",
        "longitude",
        "maps_url",
        "name",
        "website",
    ]

    # A regular expression for matching against the denomination constants
    _DENOMINATIONS_REGEX = re.compile(
        "|".join(sorted(
            [d.value for d in constants.Denomination],
            key=lambda d: len(d),
            reverse=True,
        )),
        re.IGNORECASE | re.UNICODE
    )
    
    def primary_data(self):
        """ Resolves the primary fields and values.
            Primary fields are used for database lookups and therefore should
            not consist of complex objects.

        Returns:
            dict: The primary fields and associated values.
        """
        data = self.python_object
        return {
            "address": data.get("address", self.resolve_address()),
            "country": data.get("country"),
            "gpid": data.get("gpid"),
            "location": {
                "type": "Point",
                "coordinates": [data.get("longitude"), data.get("latitude")],
                "latitude": data.get("latitude"),
                "longitude": data.get("longitude"),
            },
            "maps_url": data.get("maps_url"),
            "name": data.get("name"),
            "phone": data.get("phone"),
            "postcode": data.get("postcode"),
            "website": data.get("website"),
        }

    def secondary_data(self):
        """ Resolves the secondary fields and values.
            Secondary fields are not necessary to uniquely identify a document.
            Secondary fields may have a greater computation complexity and are
            only intended to be computed prior to insertion.

        Returns:
            dict: The secondary fields and associated values.
        """
        return {
            "denomination": self.resolve_denomination(),
        }

    def resolve_address(self):
        """ Attempts to resolve an address for the church from latitude and
            longitude coordinates.

        Returns:
            (str): The resolved address, or None.
        """
        data = self.python_object
        results = google.reverse_geocode(
            data.get("latitude"), data.get("longitude")
        )
        return next((
            r for r in results 
            if r.get("vicinity", r.get("formatted_address"))
        ), None)

    def resolve_denomination(self):
        """ Attempts to resolve a denomination for the church.
            Inspects the name (and optionally the website as a fallback) for
            denomination-string matches.

        Returns:
            (str): The resolved denomination, or None.
        """
        data = self.python_object
        return (
            self.resolve_denomination_from_text(data.get("name")) or
            self.resolve_denomination_from_website(data.get("website"))
        )

    @classmethod
    def accepts(cls, obj):
        """ Returns true if this handler can accept the specified object.

        Args:
            (obj, object): Any provided python object.
        Returns:
            bool: True if the handler can handle the provided object.
        """
        if not isinstance(obj, dict):
            return False
        for key in cls._REQUIRED_ATTRIBUTES:
            if not key in obj:
                return False
            value = obj.get(key)
            if value in (None, ""):
                return False
        return True

    @classmethod
    def collection(cls):
        """ Returns the database collection name associated with this handler.
            This property must be overridden by subclasses.

        Returns:
            (str): The collection name.
        """
        return constants.Collection.CHURCHES.value

    @classmethod
    def resolve_denomination_from_text(cls, text):
        """ Attempts to extract a Church denomination from given text. 
            For a full list of denominations, refer to:
            `windwords.constants.Denomination`

        Args:
            text (str): Given text.
        Returns:
            str: The resolved denomination (with the most matches).
        """
        matches = [
            match.lower()
            for match in re.findall(cls._DENOMINATIONS_REGEX, text) or []
        ]
        for match in Counter(matches).most_common():
            value, count = match
            return next((
                denomination.value for denomination in constants.Denomination
                if denomination.value.lower() == value.lower()
            ), None)
        return None

    @classmethod
    def resolve_denomination_from_website(cls, url):
        """ Attempts to extract a Church denomination from the given webpage. 
            For a full list of denominations, refer to:
            `windwords.constants.Denomination`

        Args:
            url (str): A website url.
        Returns:
            str: The resolved denomination (with the most matches).
        """
        response = requests.get(url)
        if not response.ok:
            # Encountered a problem trying to load URL
            LOGGER.error(f"Request response failed for webpage: `{url}`")
            return None
        soup = BeautifulSoup(response.content, 'html.parser')
        text = f"{soup.title.text} "
        text += soup.get_text(" ", strip=True).replace("\n", " ")
        return cls.resolve_denomination_from_text(text)

    @classmethod
    def from_google_place_id(cls, gpid):
        """ Instantiates a ChurchHandler from a Google Place Id.
        
        Args:
            gpid (str): A valid Google Place API id
        Returns:
            ChurchHandler: The handler.
        Raises:
            ValueError:
                If a corresponding Google Place could not be resolved, or
                If the corresponding Google Place is not recognised as a church
        """
        # Resolve the place
        place = google.get_place(gpid) or {}
        result = place.get("result", {})
        if not result:
            raise ValueError(f"Could not resolve a Google Place for `{gpid}`")
        # Assert that the place is listed as a church or place of worship!
        types = result.get("types", [])
        if not any([t in types for t in ("church", "place_of_worship")]):
            raise ValueError(
                f"Cannot accept `{gpid}`: "
                "Place is not a church or a place of worship"
            )
        location = result.get("geometry", {}).get("location", {}) 
        address_components = result.get("address_components", [])
        # Utility to extract the address component from the JSON data
        def extract_address_component(component_name):
            return next((
                c.get("long_name") for c in address_components
                if component_name in c.get("types", [])
                ), None
            )
        # Return a dictionary with the extracted data
        return cls({
            "address": result.get("vicinity", result.get("formatted_address")),
            "country": extract_address_component("country"),
            "gpid": result.get("place_id"),
            "latitude": location.get("lat"),
            "longitude": location.get("lng"),
            "maps_url": result.get("url"),
            "name": result.get("name"),
            "phone": result.get(
                "international_phone_number",
                result.get("formatted_phone_number")
            ),
            "postcode": extract_address_component("postal_code"),
            "website": result.get("website"),
        })
