"""Module with common response entities."""

import logging


class ResponseError(Exception):
    """Exception raised due to an error in response processing (creation, handling, etc.)."""


class ResponseParseError(ResponseError):
    """Exception raised in case when a response can't be created from the provided data."""


class ResponseSerializeError(ResponseError):
    """Exception raised in case when a response can't be serialized."""


class ResponseFactory:
    """Factory to register and create different types of responses."""

    def __init__(self):
        self._parsers = {}
        self._serializers = {}

    def register_response(self, response_type, parser, serializer):
        """Register new response type.

        :param response_type: string for response type.
        :param parser: callable that converts JSON data into a response object.
        :param serializer: callable that converts a response into JSON data.
        """
        self._parsers[response_type] = parser
        self._serializers[response_type] = serializer
        logging.getLogger(__name__).info("Response type '%s' has been registered", response_type)

    def parse_response(self, data):
        """Create a response from data.

        :param data: data with response information.
        :returns: new response.
        :raises: :class:`ResponseParseError`,
            if response_type has not been registered or data is invalid.
        :raises: :class:`ResponseError` if exception is raised during creation of the response.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to parse a response")
        try:
            response_type = data["response_type"]
        except TypeError as error:
            raise ResponseParseError("Failed to parse response type. Wrong data format") from error
        except KeyError as error:
            raise ResponseParseError("Failed to parse response. Type is not specified") from error

        response_parser = self._parsers.get(response_type)
        if response_parser is None:
            message = "Failed to parse response. Unknown type '{0}'".format(response_type)
            raise ResponseParseError(message)
        logger.debug("Response parser for type '%s' has been obtained", response_type)

        try:
            parameters = data["parameters"]
        except KeyError as error:
            message = "Failed to parse response. Parameters are not specified"
            raise ResponseParseError(message) from error

        try:
            response = response_parser(response_type, parameters)
        except ResponseParseError:
            logger.exception(
                "Invalid data have been specified for response of type '%s'",
                response_type,
                )
            raise
        except Exception as error:
            logger.exception("Failed to create a response of type '%s'", response_type)
            raise ResponseError("Failed to create a response") from error
        else:
            logger.info("Successfully parsed response %s", response)

        return response

    def serialize_response(self, response):
        """Create a dictionary from a response.

        :param response: response to dump.
        :returns: dictionary with parameters of the response.
        :raises: :class:`ResponseSerializeError`,
            if response does not have type, its type has not been registered or
            response has unserializable data.
        :raises: :class:`ResponseError` if exception is raised during serialization of the response.
        """
        logger = logging.getLogger(__name__)
        logger.debug("Try to serialize response %s", response)

        try:
            response_type = response.response_type
        except AttributeError as error:
            raise ResponseSerializeError("Failed to obtain type of the response") from error

        response_serializer = self._serializers.get(response_type)
        if response_serializer is None:
            message = "Failed to serialize response {response}. Unknown type '{response_type}'".format(     # pylint: disable=line-too-long
                response=response,
                response_type=response_type,
                )
            raise ResponseSerializeError(message)

        logger.debug("Response serializer for type '%s' has been obtained", response_type)

        try:
            response_parameters = response_serializer(response_type, response)
        except ResponseSerializeError:
            logger.exception("Response %s can't be serialized", response)
            raise
        except Exception as error:
            logger.exception("Failed to serialize response %s", response)
            raise ResponseError("Failed to serialize a response") from error
        else:
            logger.info("Response of type '%s' has been successfully serialized", response_type)

        return {
            "response_type": response_type,
            "parameters": response_parameters,
            }
