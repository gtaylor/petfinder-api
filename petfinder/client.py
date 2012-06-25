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
from petfinder.exceptions import _get_exception_class_from_status_code, RecordDoesNotExistError

logger = logging.getLogger(__name__)

class PetFinderClient(object):
    """
    Simple client for the Petfinder API. You'll want to pull your API details
    from http://www.petfinder.com/developers/api-key and instantiate this
    class with said credentials.

    Refer to http://www.petfinder.com/developers/api-docs for the required
    kwargs for each method. It is safe to ignore the ``key`` argument, as this
    client handles setting that for you.
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
        if not self.endpoint.endswith("/"):
            self.endpoint += "/"

    def _do_api_call(self, method, data):
        """
        Convenience method to carry out a standard API call against the
        Petfinder API.

        :param basestring method: The API method name to call.
        :param dict data: Key/value parameters to send to the API method.
            This varies based on the method.
        :raises: A number of :py:exc:`petfinder.exceptions.PetfinderAPIError``
            sub-classes, depending on what went wrong.
        :rtype: lxml.etree._Element
        :returns: The parsed document.
        """

        # Developer API keys, auth tokens, and other standard, required args.
        data.update({
            "key": self.api_key,
            # No API methods currently use this, but we're ready for it,
            # should that change.
            "token": self.api_auth_token,
        })

        # Ends up being a full URL+path.
        url = "%s%s" % (self.endpoint, method)
        # Bombs away!
        response = requests.get(url, params=data)

        # Parse and return an ElementTree instance containing the document.
        root = etree.fromstring(response.content)

        # If this is anything but '100', it's an error.
        status_code = root.find("header/status/code").text
        # If this comes back as non-None, we know we've got problems.
        exc_class = _get_exception_class_from_status_code(status_code)
        if exc_class:
            # Sheet, sheet, errar! Raise the appropriate error, and pass
            # the accompanying error message as the exception message.
            error_message = root.find("header/status/message").text
            #noinspection PyCallingNonCallable
            raise exc_class(error_message)

        return root

    def _do_autopaginating_api_call(self, method, kwargs, parser_func):
        """
        Given an API method, the arguments passed to it, and a function to
        hand parsing off to, loop through the record sets in the API call
        until all records have been yielded.

        This is mostly done this way to reduce duplication through the various
        API methods.

        :param basestring method: The API method on the endpoint.
        :param dict kwargs: The kwargs from the top-level API method.
        :param callable parser_func: A callable that is used for parsing the
            output from the API call.
        :rtype: generator
        :returns: Returns a generator that may be returned by the top-level
            API method.
        """
        # Used to determine whether to fail noisily if no results are returned.
        has_records = {"has_records": False}

        while True:
            try:
                root = self._do_api_call(method, kwargs)
            except RecordDoesNotExistError:
                if not has_records["has_records"]:
                    # No records seen yet, this really is empty.
                    raise
                    # We've seen some records come through. We must have hit the
                # end of the result set. Finish up silently.
                return

            # This is used to track whether this go around the call->parse
            # loop yielded any records.
            records_returned_by_this_loop = False
            for record in parser_func(root, has_records):
                yield record
                # We saw a record, mark our tracker accordingly.
                records_returned_by_this_loop = True
                # There is a really fun bug in the Petfinder API with
            # shelter.getpets where an offset is returned with no pets,
            # causing an infinite loop.
            if not records_returned_by_this_loop:
                return

            # This will determine at what offset we start the next query.
            last_offset = root.find("lastOffset").text
            kwargs["offset"] = last_offset

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
            "age", "sex", "size", "description", "status", "lastUpdate",
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

    def breed_list(self, **kwargs):
        """
        breed.list wrapper. Returns a list of breed name strings.

        :rtype: list
        :returns: A list of breed names.
        """

        root = self._do_api_call("breed.list", kwargs)

        breeds = []
        for breed in root.find("breeds"):
            breeds.append(breed.text)
        return breeds

    def pet_get(self, **kwargs):
        """
        pet.get wrapper. Returns a record dict for the requested pet.

        :rtype: dict
        :returns: The pet's record dict.
        """
        root = self._do_api_call("pet.get", kwargs)

        return self._parse_pet_record(root.find("pet"))

    def pet_getrandom(self, **kwargs):
        """
        pet.getRandom wrapper. Returns a record dict or Petfinder ID
        for a random pet.

        :rtype: dict or str
        :returns: A dict of pet data if ``output`` is ``'basic'`` or ``'full'``,
            and a string if ``output`` is ``'id'``.
        """
        root = self._do_api_call("pet.getRandom", kwargs)

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
        :raises: :py:exc:`petfinder.exceptions.LimitExceeded` once
            you have reached the maximum number of records your credentials
            allow you to receive.
        """

        def pet_find_parser(root, has_records):
            """
            The parser that is used with the ``_do_autopaginating_api_call``
            method for auto-pagination.

            :param lxml.etree._Element root: The root Element in the response.
            :param dict has_records: A dict that we track the loop state in.
                dicts are passed by references, which is how this works.
            """
            for pet in root.findall("pets/pet"):
                # This is changed in the original record, since it's passed
                # by reference.
                has_records["has_records"] = True
                yield self._parse_pet_record(pet)

        return self._do_autopaginating_api_call(
            "pet.find", kwargs, pet_find_parser
        )

    def shelter_find(self, **kwargs):
        """
        shelter.find wrapper. Returns a generator of shelter record dicts
        matching your search criteria.

        :rtype: generator
        :returns: A generator of shelter record dicts.
        :raises: :py:exc:`petfinder.exceptions.LimitExceeded` once you have
            reached the maximum number of records your credentials allow you
            to receive.
        """

        def shelter_find_parser(root, has_records):
            """
            The parser that is used with the ``_do_autopaginating_api_call``
            method for auto-pagination.

            :param lxml.etree._Element root: The root Element in the response.
            :param dict has_records: A dict that we track the loop state in.
                dicts are passed by references, which is how this works.
            """
            for shelter in root.find("shelters"):
                has_records["has_records"] = True
                record = {}
                for field in shelter:
                    record[field.tag] = field.text
                yield record

        return self._do_autopaginating_api_call(
            "shelter.find", kwargs, shelter_find_parser
        )

    def shelter_get(self, **kwargs):
        """
        shelter.get wrapper. Given a shelter ID, retrieve its details in
        dict form.

        :rtype: dict
        :returns: The shelter's details.
        """

        root = self._do_api_call("shelter.get", kwargs)

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
        :raises: :py:exc:`petfinder.exceptions.LimitExceeded` once you have
            reached the maximum number of records your credentials allow you
            to receive.
        """

        def shelter_getpets_parser_ids(root, has_records):
            """
            Parser for output=id.
            """
            pet_ids = root.findall("petIds/id")
            for pet_id in pet_ids:
                yield pet_id.text

        def shelter_getpets_parser_records(root, has_records):
            """
            Parser for output=full or output=basic.
            """
            for pet in root.findall("pets/pet"):
                yield self._parse_pet_record(pet)


        # Depending on the output value, select the correct parser.
        if kwargs.get("output", "id") == "id":
            shelter_getpets_parser = shelter_getpets_parser_ids
        else:
            shelter_getpets_parser = shelter_getpets_parser_records

        return self._do_autopaginating_api_call(
            "shelter.getPets", kwargs, shelter_getpets_parser
        )

    def shelter_listbybreed(self, **kwargs):
        """
        shelter.listByBreed wrapper. Given a breed and an animal type, list
        the shelter IDs with pets of said breed.

        :rtype: generator
        :returns: A generator of shelter IDs that have breed matches.
        """

        root = self._do_api_call("shelter.listByBreed", kwargs)

        shelter_ids = root.findall("shelterIds/id")
        for shelter_id in shelter_ids:
            yield shelter_id.text
