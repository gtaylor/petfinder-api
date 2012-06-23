import unittest
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