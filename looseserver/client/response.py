"""Module to work with responses."""


class ClientResponse:
    """Class to manage a response by the client."""

    def __init__(self, response_type):
        self._type = response_type

    @property
    def response_type(self):
        """Type of the response."""
        return self._type
