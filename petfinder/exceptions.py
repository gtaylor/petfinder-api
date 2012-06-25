"""
Petfinder API exceptions.
"""

class PetfinderAPIError(Exception):
    """
    Base class for all Petfinder API exceptions. Mostly here to allow end
    users to catch all Petfinder exceptions.
    """

    pass


class InvalidRequestError(PetfinderAPIError):
    """
    Raised when an invalid or mal-formed request is sent.
    """

    pass


class RecordDoesNotExistError(PetfinderAPIError):
    """
    Raised when querying for a record that does not exist.
    """

    pass


class LimitExceeded(PetfinderAPIError):
    """
    Raised when usage limits are exceeded.
    """

    pass


class InvalidGeographicalLocationError(PetfinderAPIError):
    """
    Raised when an invalid geographical location is specified.
    """

    pass


class RequestIsUnauthorizedError(PetfinderAPIError):
    """
    Raised when attempting to call a method that the user is unauthorized for.
    """

    pass


class AuthenticationFailure(PetfinderAPIError):
    """
    Raised when an authentication failure occurs.
    """

    pass


class GenericInternalError(PetfinderAPIError):
    """
    Your guess is as good as mine.
    """

    pass


class UnrecognizedError(PetfinderAPIError):
    """
    This is raised if the API returns a status code that we don't have a
    matching exception for. This is more for future-proofing, in case they
    add extra status codes.
    """

    pass


# Maps status codes to exceptions.
STATUS_CODE_MAPPING = {
    '200': InvalidRequestError,
    '201': RecordDoesNotExistError,
    '202': LimitExceeded,
    '203': InvalidGeographicalLocationError,
    '300': RequestIsUnauthorizedError,
    '301': AuthenticationFailure,
    '999': GenericInternalError,
    'UNKNOWN': UnrecognizedError,
}


def _get_exception_class_from_status_code(status_code):
    """
    Utility function that accepts a status code, and spits out a reference
    to the correct exception class to raise.

    :param str status_code: The status code to return an exception class for.
    :rtype: PetfinderAPIError or None
    :returns: The appropriate PetfinderAPIError subclass. If the status code
        is not an error, return ``None``.
    """
    if status_code == '100':
        return None

    exc_class = STATUS_CODE_MAPPING.get(status_code)
    if not exc_class:
        # No status code match, return the "I don't know wtf this is"
        # exception class.
        return STATUS_CODE_MAPPING['UNKNOWN']
    else:
        # Match found, yay.
        return exc_class