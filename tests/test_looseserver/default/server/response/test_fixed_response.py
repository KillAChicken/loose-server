"""Test cases for FixedResponse."""

import pytest

from looseserver.default.common.constants import ResponseType
from looseserver.default.common.configuration import ResponseFactoryPreparator
from looseserver.default.server.response import FixedResponse


def test_response_representation():
    """Check the representation of the fixed response.

    1. Create a fixed response.
    2. Check result of the repr function.
    """
    status = 200
    headers = {"key": "value"}
    body = "body"
    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=status,
        headers=headers,
        body=body,
        )
    assert repr(response) == "FixedResponse()", "Wrong representation"


@pytest.mark.parametrize(
    argnames="status",
    argvalues=[200, 300, 400, 500],
    ids=["Success", "Redirect", "Bad Request", "Server Error"],
    )
def test_status(
        base_endpoint,
        server_response_factory,
        configured_application_client,
        apply_response,
        status
    ):
    """Check that status can be set by fixed respone.

    1. Prepare fixed response in the response factory.
    2. Create a fixed response with specified status.
    3. Create an universal rule and set the response for it.
    4. Make a request to the base endpoint.
    5. Check status of the response.
    """
    preparator = ResponseFactoryPreparator(server_response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=status,
        headers={},
        body="",
        )
    apply_response(response)

    http_response = configured_application_client.get(base_endpoint)
    assert http_response.status_code == status, "Wrong status code"


@pytest.mark.parametrize(
    argnames="headers",
    argvalues=[
        {},
        {"key": "value"},
        {
            "first": "value",
            "second": "value",
            },
        ],
    ids=[
        "Empty headers",
        "Single header",
        "Several headers",
        ]
    )
def test_headers(
        base_endpoint,
        server_response_factory,
        configured_application_client,
        apply_response,
        headers,
    ):
    """Check that headers can be set by fixed respone.

    1. Prepare fixed response in the response factory.
    2. Create a fixed response with specified headers.
    3. Create an universal rule and set the response for it.
    4. Make a request to the base endpoint.
    5. Check that response contains specified headers.
    """
    preparator = ResponseFactoryPreparator(server_response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers=headers,
        body="",
        )
    apply_response(response)

    http_response = configured_application_client.get(base_endpoint)
    assert set(headers.items()).issubset(http_response.headers.items()), "Headers were not set"


@pytest.mark.parametrize(
    argnames="body",
    argvalues=["", "body"],
    ids=["Empty", "Non-empty"],
    )
def test_string_body(
        base_endpoint,
        server_response_factory,
        configured_application_client,
        apply_response,
        body,
    ):
    """Check that body can be set by fixed respone.

    1. Prepare fixed response in the response factory.
    2. Create a fixed response with specified string body.
    3. Create an universal rule and set the response for it.
    4. Make a request to the base endpoint.
    5. Check that response contains specified headers.
    """
    preparator = ResponseFactoryPreparator(server_response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers={},
        body=body,
        )
    apply_response(response)

    http_response = configured_application_client.get(base_endpoint)
    assert http_response.data == body.encode("utf8"), "Wrong body"


@pytest.mark.parametrize(
    argnames="body",
    argvalues=[b"", b"body"],
    ids=["Empty", "Non-empty"],
    )
def test_bytes_body(
        base_endpoint,
        server_response_factory,
        configured_application_client,
        apply_response,
        body,
    ):
    """Check that body can be set by fixed respone.

    1. Prepare fixed response in the response factory.
    2. Create a fixed response with specified bytes body.
    3. Create an universal rule and set the response for it.
    4. Make a request to the base endpoint.
    5. Check that response contains specified headers.
    """
    preparator = ResponseFactoryPreparator(server_response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers={},
        body=body,
        )
    apply_response(response)

    http_response = configured_application_client.get(base_endpoint)
    assert http_response.data == body, "Wrong body"
