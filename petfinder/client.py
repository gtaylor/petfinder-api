"""
The PetFinderAPI class here is the main event. Instantiate it with the
correct parameters and get off to the races. Make sure to go check out the
developer site on Petfinder:

http://www.petfinder.com/developers
"""

import logging
import requests
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
        breed.list wrapper. Returns a generator of breed record dicts matching
        your search criteria.

        :rtype: generator
        :returns: A generator of breed record dicts.
        """

        root = self._call_api('breed.list', kwargs)

        breeds = []
        for breed in root.find("breeds"):
            breeds.append(breed.text)
        return breeds

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

        root = self._call_api('shelter.get', kwargs)

        shelter = root.find("shelter")
        for field in shelter:
            record = {}
            for field in shelter:
                record[field.tag] = field.text
            return record