"""Test cases for FixedResponse."""

from urllib.parse import urljoin

import pytest

from looseserver.server.application import configure_application
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
def test_status(rule_factory, response_factory, rule_match_all, status):
    """Check that status can be set by fixed respone.

    1. Prepare fixed response in the response factory.
    2. Configure application with the response factory.
    3. Create a rule that matches every request.
    4. Make a POST-request to set a fixed response with specified status.
    5. Make a request to the base endpoint.
    6. Check status of the response.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    serialized_rule = rule_factory.serialize_rule(rule=rule_match_all)

    client = application.test_client()

    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=status,
        headers={},
        body="",
        )
    serialized_response = response_factory.serialize_response(response=response)

    http_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    assert client.get(base_endpoint).status_code == status, "Wrong status code"


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
def test_headers(rule_factory, response_factory, rule_match_all, headers):
    """Check that headers can be set by fixed respone.

    1. Prepare fixed response in the response factory.
    2. Configure application with the response factory.
    3. Create a rule that matches every request.
    4. Make a POST-request to set a fixed response with specified status.
    5. Make a request to the base endpoint.
    6. Check that response contains specified headers.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    serialized_rule = rule_factory.serialize_rule(rule=rule_match_all)

    client = application.test_client()

    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers=headers,
        body="",
        )
    serialized_response = response_factory.serialize_response(response=response)

    http_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    http_response = client.get(base_endpoint)

    assert set(headers.items()).issubset(http_response.headers.items()), "Headers were not set"


@pytest.mark.parametrize(
    argnames="body",
    argvalues=["", "body"],
    ids=["Empty", "Non-empty"],
    )
def test_body(rule_factory, response_factory, rule_match_all, body):
    """Check that headers can be set by fixed respone.

    1. Prepare fixed response in the response factory.
    2. Configure application with the response factory.
    3. Create a rule that matches every request.
    4. Make a POST-request to set a fixed response with specified status.
    5. Make a request to the base endpoint.
    6. Check that response contains specified headers.
    """
    base_endpoint = "/base/"
    configuration_endpoint = "/config/"

    preparator = ResponseFactoryPreparator(response_factory)
    preparator.prepare_fixed_response(fixed_response_class=FixedResponse)

    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    serialized_rule = rule_factory.serialize_rule(rule=rule_match_all)

    client = application.test_client()

    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers={},
        body=body,
        )
    serialized_response = response_factory.serialize_response(response=response)

    http_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )
    assert http_response.status_code == 200, "Can't set a response"

    assert client.get(base_endpoint).data == body.encode("utf8"), "Wrong body"
