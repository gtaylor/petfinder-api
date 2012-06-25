.. _quickstart:

.. include:: global.txt

Quickstart
==========

This section goes over how to get up and running quickly. We'll assume that
you have already followed the :doc:`installation` instructions, and are
ready to go.

Petfinder.com credentials
-------------------------

Before you can make your first query to Petfinder, you'll need to obtain a set
of API credentials. You can get them from the `Petfinder API`_ page. You'll need
to register first.

Jot down your *API Key* and *API Secret* for use in the next step.

Instantiate the API client
--------------------------

Next, you'll want to import the module::

    >>> import petfinder

Then instantiate the API client with your Petfinder.com API credentials::

    >>> api = petfinder.PetFinderClient(api_key='yourkey', api_secret='yoursecret')

You are now ready to query against the Petfinder API::

    >>> breeds = api.breed_list(animal="dog")

See :doc:`reference` for a full list of methods. We support all of the
query methods on the Petfinder API. Please do continue reading the next
few sections in this quickstart for some important tidbits.

How to determine kwargs for API methods
---------------------------------------

petfinder-api is a very thin wrapper around the Petfinder API. We point
developers to the `Petfinder API docs`_ for all of the required/optional
keywords, instead of duplicating it all here.

For example, look at the ``pet.find`` method on the `Petfinder API docs`_.
This maps to our :py:meth:`petfinder.PetFinderClient.pet_find` method. You can
ignore any of the ``key`` arguments, since petfinder-api sets that for you.
The only required parameter for ``pet.find`` is ``location``. Here's a minimal
example::

    for pet in api.pet_find(location="29678"):
        # This will be a pet record in the form of a dict.
        print(pet)

To outline a process for this, first determine which method in
:doc:`reference` you'll want to use:

1. Reference the beginning of the docstring for which Petfinder API call it
   wraps. For example,  :py:meth:`petfinder.PetFinderClient.pet_find` wraps ``pet.find``.
2. Refer to the `Petfinder API docs`_ for the required kwargs.

Many calls return generators
----------------------------

An extremely important thing to note is that many of the calls return Python
generators. This is the most efficient way for us to paginate through multiple
pages of results (behind the scenes). Make sure to note the return types
for whatever API client method you're calling. More details can be found in
:doc:`reference`.

Auto-pagination of results
--------------------------

Another thing to keep in mind is that the petfinder-api client auto-paginates
through results. The ``count`` parameter in the Petfinder API determines how
many results are returned per "page". petfinder-api will happily continue to
make additional API requests if you continue to iterate over the generators
it returns. This will often continue until you see the infamous
:py:exc:`petfinder.exceptions.LimitExceeded` exception, which you will hit
on pretty much any ``*_find`` call, and some ``*_list`` calls.

The important thing to consider is that a higher ``count`` will result in larger,
but fewer HTTP requests to the Petfinder API, whereas smaller values will result
in more frequent, but smaller requests from the API.