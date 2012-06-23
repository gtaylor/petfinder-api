import unittest
import datetime
from pprint import pprint
from petfinder.exceptions import InvalidRequestError, LimitExceeded
from tests.api_details import API_DETAILS
import petfinder

#noinspection PyClassicStyleClass
class BaseCase(unittest.TestCase):
    """
    Base test case for all API tests. Sets up the API instance and other boring
    stuff.
    """

    def setUp(self):
        """
        This is executed for every unit test.
        """

        self.api = petfinder.PetFinderClient(
            api_key=API_DETAILS['API_KEY'],
            api_secret=API_DETAILS['API_SECRET']
        )

    def _check_pet_record(self, record):
        """
        Given a pet record dict, make sure it's got some important fields.

        :param dict record: The pet record to check.
        """
        self.assertTrue(record.has_key("id"))
        self.assertTrue(record.has_key("name"))
        self.assertIsInstance(record["lastUpdate"], datetime.datetime)


#noinspection PyClassicStyleClass
class PetTests(BaseCase):
    """
    Tests for pet-related methods.
    """

    def test_pet_getrandom(self):
        """
        Tests the pet_getrandom() method.
        """

        # output=full shows a full record.
        record = self.api.pet_getrandom(output="full")
        self._check_pet_record(record)

        # output=full shows a full record.
        record = self.api.pet_getrandom(output="basic")
        self._check_pet_record(record)

        # If output=id, we should get a random pet ID string.
        random_pet_id = self.api.pet_getrandom(output="id")
        self.assertIsInstance(random_pet_id, basestring)

    def test_pet_get(self):
        """
        Tests the pet_get() method.
        """

        # The ID seen here is the Petfinder ID, not the shelter's ID.
        record = self.api.pet_get(id=23220812)
        self._check_pet_record(record)

    def test_pet_find(self):
        """
        Tests the pet_find() method.
        """

        try:
            for record in self.api.pet_find(
                animal="dog", location="29678", output="basic",
                breed="Treeing Walker Coonhound", count=200,
            ):
                self._check_pet_record(record)
        except LimitExceeded:
            # We'll eventually hit this.
            pass


#noinspection PyClassicStyleClass
class ShelterTests(BaseCase):
    """
    Tests for the shelter-related methods.
    """

    def test_shelter_find(self):
        """
        Tests the shelter_find() method.
        """

        try:
            for shelter in self.api.shelter_find(location='30127', count=500):
                self.assertIsInstance(shelter, dict)
                self.assertTrue(shelter.has_key('id'))
                self.assertTrue(shelter.has_key('name'))
        except LimitExceeded:
            # We'll eventually hit this.
            pass

    def test_shelter_get(self):
        """
        Tests the shelter_get() method.
        """

        shelter = self.api.shelter_get(id='GA137')
        self.assertIsInstance(shelter, dict)
        self.assertTrue(shelter.has_key('id'))
        self.assertTrue(shelter.has_key('name'))

    def test_shelter_getpets(self):
        """
        Tests the shelter_getpets() method.
        """

        try:
            # This returns a generator of pet record dicts.
            for record in self.api.shelter_getpets(id="GA137", output="basic"):
                self._check_pet_record(record)
        except LimitExceeded:
            # We'll eventually hit this.
            pass

        try:
            # This returns a generator of pet ID strings.
            for pet_id in self.api.shelter_getpets(id="GA137", output="id"):
                self.assertIsInstance(pet_id, basestring)
        except LimitExceeded:
            # We'll eventually hit this.
            pass

    def test_shelter_listbybreed(self):
        """
        Tests the shelter_listbybreed() call.
        """

        # Disable this test for now, as this call appears to be broken on
        # the Petfinder API.
        return
        # This returns a generator of shelter IDs.
        for shelter_id in self.api.shelter_listbybreed(
            animal="dog", breed="Pug",
        ):
            self.assertIsInstance(shelter_id, basestring)

#noinspection PyClassicStyleClass
class BreedTests(BaseCase):
    """
    Tests for breed-related methods.
    """

    def test_breed_list(self):
        """
        Tests breed listing.
        """
        breeds = self.api.breed_list(animal="dog")
        self.assertIsInstance(breeds, list)
        self.assertTrue("American Bulldog" in breeds)

        # What animal is das?
        self.assertRaises(InvalidRequestError,
            self.api.breed_list,
                animal="aliens"
        )
