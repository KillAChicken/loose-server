"""Test cases for looseserver common response entities."""

from collections import namedtuple

import pytest

from looseserver.common.response import (
    ResponseFactory,
    ResponseError,
    ResponseParseError,
    ResponseSerializeError,
    )


ResponseClass = namedtuple("ResponseClass", "response_type parameters")


def test_parse_response():
    """Check that registered parser is used by response factory.

    1. Create response factory.
    2. Register new response type.
    3. Parse a response.
    4. Check that the response is successfully parsed.
    """
    response_factory = ResponseFactory()
    parser = lambda response_type, response_data: (response_type, response_data)

    response_type = "Test"
    response_factory.register_response(response_type=response_type, parser=parser, serializer=None)

    response_parameters = {
        "key": "value",
        }
    response_data = {
        "response_type": response_type,
        "parameters": response_parameters,
        }

    parsed_response = response_factory.parse_response(data=response_data)
    assert parsed_response == (response_type, response_parameters), "Response has not been parsed"


def test_parse_wrong_data_type():
    """Check that ResponseParseError is raised on attempt to parse wrong data type.

    1. Create response factory.
    2. Register new response type.
    3. Try to parse a response from an object that without __getitem__.
    4. Check that ResponseParseError is raised.
    5. Check the message of the error.
    """
    response_factory = ResponseFactory()
    parser = lambda *args, **kwargs: None

    response_factory.register_response(response_type="Test", parser=parser, serializer=None)

    with pytest.raises(ResponseParseError) as exception_info:
        response_factory.parse_response(data=None)

    assert exception_info.value.args[0] == "Failed to parse response type. Wrong data format", (
        "Wrong error message"
        )


def test_parse_data_without_type():
    # pylint: disable=line-too-long
    """Check that ResponseParseError is raised on attempt to parse dictionary without "response_type" key.

    1. Create response factory.
    2. Register new response type.
    3. Try to parse a response from a dictionary without "response_type" key.
    4. Check that ResponseParseError is raised.
    5. Check the message of the error.
    """
    # pylint: enable=line-too-long
    response_factory = ResponseFactory()
    parser = lambda *args, **kwargs: None

    response_factory.register_response(response_type="Test", parser=parser, serializer=None)

    with pytest.raises(ResponseParseError) as exception_info:
        response_factory.parse_response(data={"parameters": {"key": "value"}})

    assert exception_info.value.args[0] == "Failed to parse response. Type is not specified", (
        "Wrong error message"
        )


def test_parse_unknown_type():
    """Check that ResponseParseError is raised on attempt to parse response of unknown type.

    1. Create response factory.
    2. Register new response type.
    3. Try to parse a response with unregistered type.
    4. Check that ResponseParseError is raised.
    5. Check the message of the error.
    """
    response_factory = ResponseFactory()
    parser = lambda *args, **kwargs: None
    response_factory.register_response(response_type="Test", parser=parser, serializer=None)

    response_data = {
        "response_type": "NonExistentType",
        "parameters": {},
        }

    with pytest.raises(ResponseParseError) as exception_info:
        response_factory.parse_response(data=response_data)

    error_message = "Failed to parse response. Unknown type 'NonExistentType'"
    assert exception_info.value.args[0] == error_message, "Wrong error message"


def test_parse_data_without_parameters():
    # pylint: disable=line-too-long
    """Check that ResponseParseError is raised on attempt to parse dictionary without "parameters" key.

    1. Create response factory.
    2. Register new response type.
    3. Try to parse a response from a dictionary without "parameters" key.
    4. Check that ResponseParseError is raised.
    5. Check the message of the error.
    """
    # pylint: enable=line-too-long
    response_factory = ResponseFactory()
    parser = lambda *args, **kwargs: None

    response_type = "Test"
    response_factory.register_response(response_type=response_type, parser=parser, serializer=None)

    with pytest.raises(ResponseParseError) as exception_info:
        response_factory.parse_response(data={"response_type": response_type})

    expected_message = "Failed to parse response. Parameters are not specified"
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_parse_response_with_error():
    """Check that ResponseParseError is propagated from parsers.

    1. Create response factory.
    2. Register a new response type with a parser, raising ResponseParseError.
    3. Try to parse a response.
    4. Check that ResponseParseError is raised.
    """
    response_factory = ResponseFactory()
    error = ResponseParseError("TestError")
    def _parser(response_type, response_data):
        # pylint: disable=unused-argument
        raise error

    response_type = "Test"
    response_factory.register_response(response_type=response_type, parser=_parser, serializer=None)

    response_data = {
        "response_type": response_type,
        "parameters": {},
        }

    with pytest.raises(ResponseParseError) as exception_info:
        response_factory.parse_response(data=response_data)

    assert exception_info.value is error, "Wrong error is raised"


def test_parse_response_with_unknown_error():
    """Check that ResponseError is raised if unhandled exception is raised by a parser.

    1. Create response factory.
    2. Register a new response type with a parser,
       raising an error different from ResponseParseError.
    3. Try to parse a response.
    4. Check that ResponseError is raised.
    """
    response_factory = ResponseFactory()
    error = ValueError("TestError")
    def _parser(response_type, response_data):
        # pylint: disable=unused-argument
        raise error

    response_type = "Test"
    response_factory.register_response(response_type=response_type, parser=_parser, serializer=None)

    response_data = {
        "response_type": response_type,
        "parameters": {},
        }

    with pytest.raises(ResponseError) as exception_info:
        response_factory.parse_response(data=response_data)

    actual_error = exception_info.value
    assert not isinstance(actual_error, ResponseParseError), "Wrong type of the error"
    assert actual_error.args[0] == "Failed to create a response", "Wrong error message"
    assert actual_error.__cause__ is error, "Wrong reason"


def test_serialize_response():
    """Check that registered serializer is used by response factory.

    1. Create response factory.
    2. Register new response type.
    3. Serialize a response.
    4. Check that the response is successfully serialized.
    """
    response_factory = ResponseFactory()
    def _serializer(response_type, response):
        return response_type, response

    response_type = "Test"
    response_factory.register_response(
        response_type=response_type,
        parser=None,
        serializer=_serializer,
        )
    response = ResponseClass(response_type=response_type, parameters={})

    expected_serialized_response = {
        "response_type": response_type,
        "parameters": (
            response_type,
            response,
            ),
        }

    serialized_response = response_factory.serialize_response(response=response)
    assert serialized_response == expected_serialized_response, "Response has not been serialized"


def test_serialize_wrong_object():
    # pylint: disable=line-too-long
    """Check that ResponseSerializeError is raised on attempt to serialize object without response_type.

    1. Create response factory.
    2. Register new response type.
    3. Try to serialize an object without response_type attribute.
    4. Check that ResponseSerializeError is raised.
    5. Check the message of the error.
    """
    # pylint: enable=line-too-long
    response_factory = ResponseFactory()
    serializer = lambda *args, **kwargs: None

    response_factory.register_response(response_type="Test", parser=None, serializer=serializer)

    with pytest.raises(ResponseSerializeError) as exception_info:
        response_factory.serialize_response(response=None)

    assert exception_info.value.args[0] == "Failed to obtain type of the response", (
        "Wrong error message"
        )


def test_serialize_unknown_type():
    """Check that ResponseSerializeError is raised on attempt to serialize response of unknown type.

    1. Create response factory.
    2. Register new response type.
    3. Try to serialize a response with unregistered type.
    4. Check that ResponseSerializeError is raised.
    5. Check the message of the error.
    """
    response_factory = ResponseFactory()
    serializer = lambda *args, **kwargs: None
    response_factory.register_response(response_type="Test", parser=None, serializer=serializer)

    response = ResponseClass(response_type="NonExistentType", parameters={})

    with pytest.raises(ResponseSerializeError) as exception_info:
        response_factory.serialize_response(response=response)

    expected_message = "Failed to serialize response {0}. Unknown type 'NonExistentType'".format(
        response,
        )
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_serialize_response_with_error():
    """Check that ResponseSerializeError is propagated from serializers.

    1. Create response factory.
    2. Register a new response type with a serializer, raising ResponseSerializeError
    3. Try to serialize a response.
    4. Check that ResponseSerializeError is raised.
    """
    response_factory = ResponseFactory()
    error = ResponseSerializeError("TestError")
    def _serializer(response_type, response):
        # pylint: disable=unused-argument
        raise error

    response_type = "Test"
    response_factory.register_response(
        response_type=response_type,
        parser=None,
        serializer=_serializer,
        )

    response = ResponseClass(response_type=response_type, parameters={})

    with pytest.raises(ResponseSerializeError) as exception_info:
        response_factory.serialize_response(response=response)

    assert exception_info.value is error, "Wrong error is raised"


def test_serialize_response_with_unknown_error():
    """Check that ResponseError is raised if unhandled exception is raised by a serializer.

    1. Create response factory.
    2. Register a new response type with a serialier,
       raising an error different from ResponseSerializeError.
    3. Try to serialize a response.
    4. Check that ResponseError is raised.
    """
    response_factory = ResponseFactory()
    error = ValueError("TestError")
    def _serializer(response_type, response):
        # pylint: disable=unused-argument
        raise error

    response_type = "Test"
    response_factory.register_response(
        response_type=response_type,
        parser=None,
        serializer=_serializer,
        )

    response = ResponseClass(response_type=response_type, parameters={})

    with pytest.raises(ResponseError) as exception_info:
        response_factory.serialize_response(response=response)

    actual_error = exception_info.value
    assert not isinstance(actual_error, ResponseSerializeError), "Wrong type of the error"
    assert actual_error.args[0] == "Failed to serialize a response", "Wrong error message"
    assert actual_error.__cause__ is error, "Wrong reason"
