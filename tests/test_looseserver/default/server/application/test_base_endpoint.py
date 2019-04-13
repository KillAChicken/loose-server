"""Test cases for base endpoint."""

import pytest

from looseserver.server.application import DEFAULT_BASE_ENDPOINT, DEFAULT_CONFIGURATION_ENDPOINT
from looseserver.client.flask import FlaskClient
from looseserver.default.server.rule import create_rule_factory
from looseserver.default.server.application import configure_application


def test_default_routes(
        client_rule_factory,
        client_response_factory,
        client_method_rule_class,
        client_fixed_response_class,
    ):
    """Check that rules are applied for all nested routes of the default base endpoint.

    1. Configure application without specifying base endpoint.
    2. Create a flask client.
    3. Create a GET-rule and set a response for it.
    4. Make a GET-request to the default endpoint.
    5. Check the response.
    """
    application = configure_application()

    client = FlaskClient(
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        base_url=DEFAULT_CONFIGURATION_ENDPOINT,
        application_client=application.test_client(),
        )

    rule_id = client.create_rule(client_method_rule_class(method="GET")).rule_id
    client.set_response(rule_id=rule_id, response=client_fixed_response_class(status=200))

    assert application.test_client().get(DEFAULT_BASE_ENDPOINT).status_code == 200, "Wrong status"


@pytest.mark.parametrize(
    argnames="specified_endpoint,expected_endpoint",
    argvalues=[
        ("/base/", "/base/"),
        ("base/", "/base/"),
        ("/base", "/base/"),
        ],
    ids=[
        "Both slashes",
        "Missing slash at the beginning",
        "Missing slash at the end",
        ],
    )
def test_routes(
        client_rule_factory,
        client_response_factory,
        client_method_rule_class,
        client_fixed_response_class,
        specified_endpoint,
        expected_endpoint,
    ):
    # pylint: disable=too-many-arguments
    """Check that rules are applied for all nested routes of the specified base endpoint.

    1. Configure application with specifying base endpoint.
    2. Create a flask client.
    3. Create a GET-rule and set a response for it.
    4. Make a GET-request to the default endpoint.
    5. Check the response.
    """
    server_rule_factory = create_rule_factory(base_url=expected_endpoint)
    application = configure_application(
        base_endpoint=specified_endpoint,
        rule_factory=server_rule_factory,
        )

    client = FlaskClient(
        rule_factory=client_rule_factory,
        response_factory=client_response_factory,
        base_url=DEFAULT_CONFIGURATION_ENDPOINT,
        application_client=application.test_client(),
        )

    rule_id = client.create_rule(client_method_rule_class(method="GET")).rule_id
    client.set_response(rule_id=rule_id, response=client_fixed_response_class(status=200))

    assert application.test_client().get(expected_endpoint).status_code == 200, "Wrong status"
