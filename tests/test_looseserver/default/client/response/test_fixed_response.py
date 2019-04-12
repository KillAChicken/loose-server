"""Test cases for FixedResponse."""

import pytest

from looseserver.default.common.constants import ResponseType
from looseserver.default.common.configuration import ResponseFactoryPreparator
from looseserver.default.client.response import FixedResponse


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


def test_default_response_type():
    """Check the default response type of the fixed response.

    1. Create a fixed response without specifying its type.
    2. Check the response type.
    """
    response = FixedResponse()
    assert response.response_type == ResponseType.FIXED.name, "Wrong response type"


def test_default_parameters():
    """Check the default values of the response.

    1. Create a fixed response without specifying anything.
    2. Check status.
    3. Check headers.
    4. Check body.
    """
    response = FixedResponse()
    assert response.status == 200, "Wrong status"
    assert response.headers == {}, "Wrong headers"
    assert response.body == "", "Wrong body"


@pytest.mark.parametrize(argnames="status", argvalues=[200, 400], ids=["Success", "Failure"])
def test_status(
        base_endpoint,
        default_factories_application,
        client_response_factory,
        configured_flask_client,
        existing_get_rule,
        status,
    ):
    # pylint: disable=too-many-arguments
    """Check that response status can be set.

    1. Prepare a fixed response in the response factory.
    2. Set a fixed response with specified status for an existing rule.
    3. Check the status of the response.
    """
    preparator = ResponseFactoryPreparator(client_response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    fixed_response = FixedResponse(status=status)
    configured_flask_client.set_response(rule_id=existing_get_rule.rule_id, response=fixed_response)

    http_response = default_factories_application.test_client().get(base_endpoint)
    assert http_response.status_code == status, "Wrong status code"


@pytest.mark.parametrize(
    argnames="headers",
    argvalues=[
        {},
        {"Header": "Value"},
        {"First-Header": "First Value", "Second-Header": "Second Value"},
        ],
    ids=["Without headers", "Single header", "Several headers"],
    )
def test_headers(
        base_endpoint,
        default_factories_application,
        client_response_factory,
        configured_flask_client,
        existing_get_rule,
        headers,
    ):
    # pylint: disable=too-many-arguments
    """Check that response headers can be set.

    1. Prepare a fixed response in the response factory.
    2. Set a fixed response with specified headers for an existing rule.
    3. Check the headers of the response.
    """
    preparator = ResponseFactoryPreparator(client_response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    fixed_response = FixedResponse(headers=headers)
    configured_flask_client.set_response(rule_id=existing_get_rule.rule_id, response=fixed_response)

    http_response = default_factories_application.test_client().get(base_endpoint)
    assert set(http_response.headers.items()).issuperset(headers.items()), (
        "Headers were not set"
        )


@pytest.mark.parametrize(argnames="body", argvalues=["", "body"], ids=["Empty", "Non-empty"])
def test_string_body(
        base_endpoint,
        default_factories_application,
        client_response_factory,
        configured_flask_client,
        existing_get_rule,
        body,
    ):
    # pylint: disable=too-many-arguments
    """Check that response body can be set as a string.

    1. Prepare a fixed response in the response factory.
    2. Set a fixed response with specified string body for an existing rule.
    3. Check the body of the response.
    """
    preparator = ResponseFactoryPreparator(client_response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    fixed_response = FixedResponse(body=body)
    configured_flask_client.set_response(rule_id=existing_get_rule.rule_id, response=fixed_response)

    http_response = default_factories_application.test_client().get(base_endpoint)
    assert http_response.data == body.encode("utf8"), "Wrong body"


@pytest.mark.parametrize(
    argnames="unicode_body,encoding",
    argvalues=[
        (u"", "utf-8"),
        (u"тело", "utf-8"),
        (u"тело", "cp1251"),
        ],
    ids=["Empty", "Non-empty utf8", "Non-empty cp1251"],
    )
def test_bytes_body(
        base_endpoint,
        default_factories_application,
        client_response_factory,
        configured_flask_client,
        existing_get_rule,
        unicode_body,
        encoding,
    ):
    # pylint: disable=too-many-arguments
    """Check that response body can be set as a bytes object.

    1. Prepare a fixed response in the response factory.
    2. Set a fixed response with specified bytes body for an existing rule.
    3. Check the body of the response.
    """
    preparator = ResponseFactoryPreparator(client_response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    body = unicode_body.encode(encoding)
    headers = {"Content-Type": "text/plain; charset={0}".format(encoding)}

    fixed_response = FixedResponse(headers=headers, body=body)
    configured_flask_client.set_response(rule_id=existing_get_rule.rule_id, response=fixed_response)

    http_response = default_factories_application.test_client().get(base_endpoint)
    assert http_response.data.decode(encoding) == unicode_body, "Wrong body"
