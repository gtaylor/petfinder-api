.. _index:

.. include:: global.txt

petfinder-api
=============

petfinder-api is a `BSD <BSD License>`_ licensed Python_ wrapper around the
`Petfinder API`_. The module handles preparing and sending API requests,
parsing the response, and returning Python objects for usage in your application.

.. code-block:: python

    import petfinder

    # Instantiate the client with your credentials.
    api = petfinder.PetFinderClient(api_key='yourkey', api_secret='yoursecret')

    # Query away!
    for shelter in api.shelter_find(location='30127', count=500):
        print(shelter['name'])

    # Search for pets.
    for pet in api.pet_find(
        animal="dog", location="29678", output="basic",
        breed="Treeing Walker Coonhound", count=200,
    ):
        print("%s - %s" % (pet['id'], pet['name']))

    # TODO: Find homes for these guys.

Assorted Info
-------------

* `Issue tracker`_ - Report bugs here.
* `GitHub project`_ - Source code lives here.
* `@gctaylor Twitter`_ - Tweets from the maintainer.

User Guide
----------

The user guide covers topics such as installation and general use of the
module. Content is largely step-by-step instructions for getting started with,
and using petfinder-api.

.. toctree::
   :maxdepth: 3

   installation
   quickstart
   reference

Indices and tables
------------------

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

