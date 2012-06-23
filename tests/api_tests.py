import unittest
from pprint import pprint
from petfinder.exceptions import InvalidRequestError
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
        self.assertTrue(record.has_key("id"))
        self.assertTrue(record.has_key("name"))

        # output=full shows a full record.
        record = self.api.pet_getrandom(output="basic")
        self.assertTrue(record.has_key("id"))
        self.assertTrue(record.has_key("name"))

        # If output=id, we should get a random pet ID string.
        random_pet_id = self.api.pet_getrandom(output="id")
        self.assertIsInstance(random_pet_id, basestring)

    def test_pet_get(self):
        """
        Tests the pet_get() method.
        """

        # The ID seen here is the Petfinder ID, not the shelter's ID.
        record = self.api.pet_get(id=23220812)
        self.assertTrue(record.has_key("id"))
        self.assertTrue(record.has_key("name"))


#noinspection PyClassicStyleClass
class ShelterTests(BaseCase):
    """
    Tests for the shelter-related methods.
    """

    def test_shelter_find(self):
        """
        Tests some simple shelter_find() calls.
        """

        for shelter in self.api.shelter_find(location='30127'):
            self.assertIsInstance(shelter, dict)
            self.assertTrue(shelter.has_key('id'))
            self.assertTrue(shelter.has_key('name'))

    def test_shelter_get(self):
        """
        Tests some simple shelter_get() calls.
        """

        shelter = self.api.shelter_get(id='GA287')
        self.assertIsInstance(shelter, dict)
        self.assertTrue(shelter.has_key('id'))
        self.assertTrue(shelter.has_key('name'))


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
