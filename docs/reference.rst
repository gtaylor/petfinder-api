.. _reference:

.. include:: global.txt

API Reference
=============

This page serves as a complete reference to all public classes and exceptions.
This is probably only useful after you have read :doc:`quickstart`.

petfinder.PetfinderClient
-------------------------

.. autoclass:: petfinder.PetFinderClient

breed_list
^^^^^^^^^^

.. automethod:: petfinder.PetFinderClient.breed_list

pet_get
^^^^^^^

.. automethod:: petfinder.PetFinderClient.pet_get


pet_getrandom
^^^^^^^^^^^^^

.. automethod:: petfinder.PetFinderClient.pet_getrandom

pet_find
^^^^^^^^

.. automethod:: petfinder.PetFinderClient.pet_find

shelter_find
^^^^^^^^^^^^

.. automethod:: petfinder.PetFinderClient.shelter_find

shelter_get
^^^^^^^^^^^

.. automethod:: petfinder.PetFinderClient.shelter_get

shelter_getpets
^^^^^^^^^^^^^^^

.. automethod:: petfinder.PetFinderClient.shelter_getpets

shelter_listbybreed
^^^^^^^^^^^^^^^^^^^

.. automethod:: petfinder.PetFinderClient.shelter_listbybreed

petfinder.exceptions
--------------------

.. automodule:: petfinder.exceptions
    :members: