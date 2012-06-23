"""
The PetFinderAPI class here is the main event. Instantiate it with the
correct parameters and get off to the races. Make sure to go check out the
developer site on Petfinder:

http://www.petfinder.com/developers
"""

import logging
import datetime
import requests
import pytz
from lxml import etree
from petfinder.exceptions import get_exception_class_from_status_code

logger = logging.getLogger(__name__)

class PetFinderClient(object):
    """
    Simple client for the Petfinder API. You'll want to pull your API details
    from http://www.petfinder.com/developers/api-key and instantiate this
    class with said credentials.
    """

    def __init__(self, api_key, api_secret, endpoint="http://api.petfinder.com/"):
        """
        :param str api_key: Your Petfinder API Key.
        :param str api_secret: Your Petfinder API Secret.
        :keyword str endpoint: Optionally, override the endpoint to send
            requests to.
        """

        self.api_key = api_key
        self.api_secret = api_secret
        # This is currently not required, but it's here for when/if they ever
        # get around to making use of it on the API service.
        self.api_auth_token = None
        self.endpoint = endpoint
        # Endpoint must end in trailing slash in order for us to tack
        # methods on the end.
        if not self.endpoint.endswith('/'):
            self.endpoint += '/'

    def _call_api(self, method, data):
        """
        Convenience method to carry out a standard API call against the
        Petfinder API.

        :param str method: The API method name to call.
        :param dict data: Key/value parameters to send to the API method.
            This varies based on the method.
        :raises: A number of PetfinderAPIError sub-classes, depending on
            what went wrong.
        :rtype: lxml.etree._Element
        :returns: The parsed document.
        """

        # Developer API keys, auth tokens, and other standard, required args.
        data.update({
            'key': self.api_key,
            # No API methods currently use this, but we're ready for it,
            # should that change.
            'token': self.api_auth_token,
        })

        # Ends up being a full URL+path.
        url = "%s%s" % (self.endpoint, method)
        # Bombs away!
        response = requests.get(url, params=data)

        print "TXT", response.content

        # Parse and return an ElementTree instance containing the document.
        root = etree.fromstring(response.content)

        # If this is anything but '100', it's an error.
        status_code = root.find("header/status/code").text
        # If this comes back as non-None, we know we've got problems.
        exc_class = get_exception_class_from_status_code(status_code)
        if exc_class:
            # Sheet, sheet, errar! Raise the appropriate error, and pass
            # the accompanying error message as the exception message.
            error_message = root.find("header/status/message").text
            #noinspection PyCallingNonCallable
            raise exc_class(error_message)

        return root

    def breed_list(self, **kwargs):
        """
        breed.list wrapper. Returns a list of breed name strings.

        :rtype: list
        :returns: A list of breed names.
        """

        root = self._call_api('breed.list', kwargs)

        breeds = []
        for breed in root.find("breeds"):
            breeds.append(breed.text)
        return breeds

    def _parse_datetime_str(self, dtime_str):
        """
        Given a standard datetime string (as seen throughout the Petfinder API),
        spit out the corresponding UTC datetime instance.

        :param str dtime_str: The datetime string to parse.
        :rtype: datetime.datetime
        :returns: The parsed datetime.
        """

        return datetime.datetime.strptime(
            dtime_str,
            "%Y-%m-%dT%H:%M:%SZ"
        ).replace(tzinfo=pytz.utc)

    def _parse_pet_record(self, root):
        """
        Given a <pet> Element from a pet.get or pet.getRandom response, pluck
        out the pet record.

        :param lxml.etree._Element root: A <pet> tag Element.
        :rtype: dict
        :returns: An assembled pet record.
        """
        record = {
            "breeds": [],
            "photos": [],
            "options": [],
            "contact": {},
        }

        # These fields can just have their keys and text values copied
        # straight over to the dict record.
        straight_copy_fields = [
            "id", "shelterId", "shelterPetId", "name", "animal", "mix",
            "age", 'sex', "size", "description", "status", "lastUpdate",
        ]

        for field in straight_copy_fields:
            # For each field, just take the tag name and the text value to
            # copy to the record as key/val.
            node = root.find(field)
            if node is None:
                print "SKIPPING %s" % field
                continue
            record[field] = node.text

        # Pets can be of multiple breeds. Find all of the <breed> tags and
        # stuff their text (breed names) into the record.
        for breed in root.findall("breeds/breed"):
            record["breeds"].append(breed.text)

        # We'll deviate slightly from the XML format here, and simply append
        # each photo entry to the record's "photo" key.
        for photo in root.findall("media/photos/photo"):
            photo = {
                "id": photo.get("id"),
                "size": photo.get("size"),
                "url": photo.text,
            }
            record["photos"].append(photo)

        # Has shots, no cats, altered, etc.
        for option in root.findall("options/option"):
            record["options"].append(option.text)

        # <contact> tag has some sub-tags that can be straight copied over.
        contact = root.find("contact")
        if contact is not None:
            for field in contact:
                record["contact"][field.tag] = field.text

        # Parse lastUpdate so we have a useable datetime.datime object.
        record["lastUpdate"] = self._parse_datetime_str(record["lastUpdate"])

        return record

    def pet_get(self, **kwargs):
        """
        pet.get wrapper. Returns a record dict for the requested pet.

        :rtype: dict
        :returns: The pet's record dict.
        """
        root = self._call_api("pet.get", kwargs)

        return self._parse_pet_record(root.find("pet"))

    def pet_getrandom(self, **kwargs):
        """
        pet.getRandom wrapper. Returns a record dict or Petfinder ID
        for a random pet.

        :rtype: dict or str
        :returns: A dict of pet data if ``output`` is ``'basic'`` or ``'full'``,
            and a string if ``output`` is ``'id'``.
        """
        root = self._call_api("pet.getRandom", kwargs)

        output_brevity = kwargs.get("output", "id")

        if output_brevity == "id":
            return root.find("petIds/id").text
        else:
            return self._parse_pet_record(root.find("pet"))

    def pet_find(self, **kwargs):
        """
        pet.find wrapper. Returns a generator of pet record dicts
        matching your search criteria.

        :rtype: generator
        :returns: A generator of pet record dicts.
        """

        root = self._call_api('pet.find', kwargs)

        for pet in root.findall("pets/pet"):
            yield self._parse_pet_record(pet)

    def shelter_find(self, **kwargs):
        """
        shelter.find wrapper. Returns a generator of shelter record dicts
        matching your search criteria.

        :rtype: generator
        :returns: A generator of shelter record dicts.
        """

        root = self._call_api('shelter.find', kwargs)

        for shelter in root.find("shelters"):
            record = {}
            for field in shelter:
                record[field.tag] = field.text
            yield record

    def shelter_get(self, **kwargs):
        """
        shelter.get wrapper. Given a shelter ID, retrieve its details in
        dict form.

        :rtype: dict
        :returns: The shelter's details.
        """

        root = self._call_api("shelter.get", kwargs)

        shelter = root.find("shelter")
        for field in shelter:
            record = {}
            for field in shelter:
                record[field.tag] = field.text
            return record

    def shelter_getpets(self, **kwargs):
        """
        shelter.getPets wrapper. Given a shelter ID, retrieve either a list of
        pet IDs (if ``output`` is ``'id'``), or a generator of pet record
        dicts (if ``output`` is ``'full'`` or ``'basic'``).

        :rtype: generator
        :returns: Either a generator of pet ID strings or pet record dicts,
            depending on the value of the ``output`` keyword.
        """

        root = self._call_api("shelter.getPets", kwargs)

        if kwargs.get("output", "id") == "id":
            pet_ids = root.findall("petIds/id")
            for pet_id in pet_ids:
                yield pet_id.text
        else:
            for pet in root.findall("pets/pet"):
                yield self._parse_pet_record(pet)

    def shelter_listbybreed(self, **kwargs):
        """
        shelter.listByBreed wrapper. Given a breed and an animal type, list
        the shelter IDs with pets of said breed.

        :rtype: generator
        :returns: A generator of shelter IDs that have breed matches.
        """

        root = self._call_api("shelter.listByBreed", kwargs)

        shelter_ids = root.findall("shelterIds/id")
        for shelter_id in shelter_ids:
            yield shelter_id.text
