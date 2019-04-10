"""Test cases for FixedResponse."""

import pytest

from looseserver.default.common.constants import ResponseType
from looseserver.default.common.configuration import ResponseFactoryPreparator
from looseserver.default.client.rule import MethodRule
from looseserver.default.client.response import FixedResponse
from looseserver.server.application import configure_application
from looseserver.client.flask import FlaskClient


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


@pytest.mark.parametrize(
    argnames="status,headers,body",
    argvalues=[
        (200, {}, ""),
        (400, {}, ""),
        (303, {"Header": "Value"}, ""),
        (404, {}, "body"),
        ],
    ids=[
        "Successful response",
        "Failed response",
        "Response with headers",
        "Response with body",
        ],
    )
def test_set_response(
        base_endpoint,
        configuration_endpoint,
        response_factory,
        status,
        headers,
        body,
    ):
    # pylint: disable=too-many-arguments
    """Check that response can be set.

    1. Configure application with default factories.
    2. Create a method rule.
    3. Prepare fixed response in the response factory of the flask client.
    4. Set a response for the rule.
    5. Check the created response.
    """
    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        )

    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    application_client = application.test_client()

    client = FlaskClient(
        base_url=configuration_endpoint,
        response_factory=response_factory,
        application_client=application_client,
        )

    rule = client.create_rule(rule=MethodRule(method="GET"))

    fixed_response = FixedResponse(
        status=status,
        headers=headers,
        body=body,
        )

    client.set_response(rule_id=rule.rule_id, response=fixed_response)

    http_response = application_client.get(base_endpoint)

    assert http_response.status_code == status, "Wrong status code"
    assert set(http_response.headers.items()).issuperset(headers.items()), "Headers were not set"
    assert http_response.data == body.encode("utf8"), "Wrong body"
