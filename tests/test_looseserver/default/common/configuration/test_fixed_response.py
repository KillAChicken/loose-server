"""Test cases to check the configuration for fixed responses."""

from collections import namedtuple
import base64

import pytest

from looseserver.common.response import ResponseParseError, ResponseSerializeError
from looseserver.default.common.constants import ResponseType
from looseserver.default.common.configuration import ResponseFactoryPreparator


_RESPONSE_FIELDS = ("status", "headers", "body")
_FixedResponse = namedtuple("FixedResponse", ["response_type"] + list(_RESPONSE_FIELDS))


def test_prepare_fixed_response(response_factory):
    """Check that fixed response can be serialized.

    1. Create preparator for a response factory.
    2. Prepare fixed response.
    3. Serialize new response.
    4. Parse serialized data.
    5. Check parsed response.
    """
    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=_FixedResponse)

    response = _FixedResponse(
        status=200,
        headers={"key": "value"},
        body="body",
        response_type=ResponseType.FIXED.name,
        )
    serialized_response = response_factory.serialize_response(response=response)

    expected_data = {
        "status": 200,
        "headers": {"key": "value"},
        "body": base64.b64encode(b"body").decode("utf8"),
        }
    assert serialized_response["parameters"] == expected_data, "Incorrect serialization"

    parsed_response = response_factory.parse_response(data=serialized_response)

    assert isinstance(parsed_response, _FixedResponse), "Wrong type of the response"
    assert parsed_response.response_type == ResponseType.FIXED.name, "Wrong response type"
    assert parsed_response.status == response.status, "Wrong status"
    assert parsed_response.headers == response.headers, "Wrong headers"
    assert parsed_response.body == response.body.encode("utf8"), "Wrong body"


@pytest.mark.parametrize(
    argnames="attribute",
    argvalues=_RESPONSE_FIELDS,
    )
def test_parse_missing_attribute(response_factory, attribute):
    """Check that ResponseParseError is raised if one of the attributes is missing.

    1. Create preparator for a response factory.
    2. Prepare fixed response.
    3. Try to parse data without one of the attributes.
    4. Check that ResponseParseError is raised.
    5. Check the error.
    """
    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=_FixedResponse)

    response = _FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers={},
        body="",
        )
    serialized_response = response_factory.serialize_response(response=response)
    serialized_response["parameters"].pop(attribute)

    with pytest.raises(ResponseParseError) as exception_info:
        response_factory.parse_response(serialized_response)

    expected_message = (
        "Response parameters must be a dictionary with keys 'body', 'status', 'headers'"
        )
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_parse_wrong_parameters_type(response_factory):
    """Check that ResponseParseError is raised if parameters are of a wrong type.

    1. Create preparator for a response factory.
    2. Prepare fixed response.
    3. Try to parse data with string parameters.
    4. Check that ResponseParseError is raised.
    5. Check the error.
    """
    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=_FixedResponse)

    response = _FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers={},
        body="body",
        )
    serialized_response = response_factory.serialize_response(response=response)
    serialized_response["parameters"] = ""

    with pytest.raises(ResponseParseError) as exception_info:
        response_factory.parse_response(serialized_response)

    expected_message = (
        "Response parameters must be a dictionary with keys 'body', 'status', 'headers'"
        )
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


@pytest.mark.parametrize(
    argnames="body",
    argvalues=["Invalid base64", list()],
    ids=["Invalid base64 string", "Invalid type"],
    )
def test_parse_wrong_body(response_factory, body):
    """Check that ResponseParseError is raised if the specified body is not base64 encoded.

    1. Create preparator for a response factory.
    2. Prepare fixed response.
    3. Try to parse data with wrong body.
    4. Check that ResponseParseError is raised.
    5. Check the error.
    """
    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=_FixedResponse)

    response = _FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers={},
        body="body",
        )
    serialized_response = response_factory.serialize_response(response=response)
    serialized_response["parameters"]["body"] = body

    with pytest.raises(ResponseParseError) as exception_info:
        response_factory.parse_response(serialized_response)

    expected_message = "Body can't be decoded with base64 encoding"
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


@pytest.mark.parametrize(
    argnames="attribute",
    argvalues=_RESPONSE_FIELDS,
    )
def test_serialize_missing_attribute(response_factory, attribute):
    """Check that ResponseSerializeError is raised if response class does not have an attribute.

    1. Create preparator for a response factory.
    2. Prepare fixed response.
    3. Try to serialize response without one of the attributes.
    4. Check that ResponseSerializeError is raised.
    5. Check the error.
    """
    fields = list(_RESPONSE_FIELDS)
    fields.remove(attribute)

    _WrongResponse = namedtuple("_WrongResponse", ["response_type"] + list(fields))

    def _create_response(**kwargs):
        kwargs.pop(attribute, None)
        return _WrongResponse(**kwargs)

    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=_create_response)

    field_values = {field: "" for field in fields}
    response = _WrongResponse(response_type=ResponseType.FIXED.name, **field_values)

    with pytest.raises(ResponseSerializeError) as exception_info:
        response_factory.serialize_response(response=response)

    expected_message = "Response must have attributes 'body', 'status' and 'headers'"
    assert exception_info.value.args[0] == expected_message, "Wrong error message"


def test_serialize_wrong_body(response_factory):
    """Check that ResponseSerializeError is raised if response body can't be encoded with base64.

    1. Create preparator for a response factory.
    2. Prepare fixed response.
    3. Try to serialize response with a list specified for the body.
    4. Check that ResponseSerializeError is raised.
    5. Check the error.
    """
    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=_FixedResponse)

    response = _FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers={},
        body=[],
        )

    with pytest.raises(ResponseSerializeError) as exception_info:
        response_factory.serialize_response(response=response)

    expected_message = "Body can't be encoded with base64 encoding"
    assert exception_info.value.args[0] == expected_message, "Wrong error message"
