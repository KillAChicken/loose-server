"""Module with common API entities."""

import enum


DEFAULT_VERSION = 1


class ResponseStatus(enum.Enum):
    """Available statuses."""
    SUCCESS = "success"
    FAILURE = "failure"


class APIError(Exception):
    """Error returned by API."""

    def __init__(self, description):
        super(APIError, self).__init__(description)
        self._description = description

    @property
    def description(self):
        """Description of the error."""
        return self._description
