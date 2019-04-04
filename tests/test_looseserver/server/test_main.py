"""Test main endpoint."""

from urllib.parse import urljoin

import pytest

from looseserver.default.common.constants import RuleType, ResponseType
from looseserver.server.run import configure_application
from looseserver.default.client.rule import MethodRule
from looseserver.default.client.response import FixedResponse
from looseserver.client.flask import FlaskClient


# pylint: disable=redefined-outer-name
@pytest.fixture
def default_application(base_endpoint, configuration_endpoint):
    """Default application."""
    return configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        )


@pytest.fixture
def default_client(configuration_endpoint, default_application):
    """Default application client."""
    return FlaskClient(
        base_url=configuration_endpoint,
        application_client=default_application.test_client(),
        )


@pytest.mark.parametrize(
    argnames="relative_path",
    argvalues=["", "children", "child/grandchild"],
    ids=["base", "child", "grandchild"],
    )
def test_routes_path(base_endpoint, default_application, default_client, relative_path):
    """Check that rules are applied for all paths.

    1. Create a rule, matching all GET-requests.
    2. Create a response for the rule.
    3. Make a GET-request to one of the nested endpoints.
    4. Check that the configured response is returned.
    """
    rule_prototype = MethodRule(rule_type=RuleType.METHOD.name, method="GET")
    rule = default_client.create_rule(rule=rule_prototype)

    response = FixedResponse(response_type=ResponseType.FIXED.name, status=200, body="Response")
    default_client.set_response(rule_id=rule.rule_id, response=response)

    url = urljoin(base_endpoint, relative_path)
    http_response = default_application.test_client().get(url)
    assert http_response.status_code == response.status, "Wrong response status"
    assert http_response.data == b"Response", "Wrong body"


def test_unmanaged_path(default_application, default_client):
    """Check that only paths nested to the base endpoint are managed.

    1. Create a rule, matching all GET-request.
    2. Create a response for the rule.
    3. Make a request to the root.
    4. Check that 404 status is returned.
    """
    rule_prototype = MethodRule(rule_type=RuleType.METHOD.name, method="GET")
    rule = default_client.create_rule(rule=rule_prototype)

    response = FixedResponse(response_type=ResponseType.FIXED.name, status=200, body="Response")
    default_client.set_response(rule_id=rule.rule_id, response=response)

    http_response = default_application.test_client().get("/")
    assert http_response.status_code == 404, "Wrong response status"
