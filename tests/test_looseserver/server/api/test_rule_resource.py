"""Test cases for the rule resourse of the looseserver API."""

import pytest

from flask import Flask
from flask_restful import Api

from looseserver.common.rule import RuleError
from looseserver.common.api import APIError
from looseserver.server.api import Rule, build_response


# pylint: disable=redefined-outer-name
@pytest.fixture
def rule_endpoint():
    """Endpoint of the rules manager resource."""
    return "/rule/{rule_id}"


@pytest.fixture
def application_client(rule_endpoint, core_manager, rule_factory):
    """Client of the configured application."""
    application = Flask("TestApplication")
    api = Api(application)
    api.add_resource(
        Rule,
        rule_endpoint.format(rule_id="<rule_id>"),
        resource_class_args=(core_manager, rule_factory),
        )
    return application.test_client()


def test_get_rule(
        core_manager,
        rule_endpoint,
        rule_factory,
        registered_rule_prototype,
        application_client,
    ):
    """Check that rule can be obtained with API.

    1. Create a rule.
    2. Make a GET request to get the rule.
    3. Check that rule is obtained.
    """
    rule_id = core_manager.add_rule(rule=registered_rule_prototype)

    http_response = application_client.get(rule_endpoint.format(rule_id=rule_id))
    assert http_response.status_code == 200, "Wrong status code"

    expected_data = rule_factory.serialize_rule(registered_rule_prototype)
    expected_data["rule_id"] = rule_id
    assert http_response.json == build_response(data=expected_data), "Wrong response"


def test_get_non_existent_rule(
        core_manager,
        rule_endpoint,
        registered_rule_prototype,
        application_client,
    ):
    """Check that error is returned if rule does not exist.

    1. Create a rule.
    2. Make a GET request to get a non-existent rule.
    3. Check that response contains an error.
    4. Check the error.
    """
    core_manager.add_rule(rule=registered_rule_prototype)

    http_response = application_client.get(rule_endpoint.format(rule_id="FakeID"))
    assert http_response.status_code == 404, "Wrong status code"

    expected_error = APIError("Failed to find rule with ID 'FakeID'")
    assert http_response.json == build_response(error=expected_error), "Wrong response"


def test_serialization_failed_unknown_error(
        core_manager,
        rule_endpoint,
        rule_factory,
        rule_prototype,
        application_client,
    ):
    """Check that error is returned if RuleError is raised on attempt to serialize a rule.

    1. Register rule type with serializer that raises RuleError.
    2. Create a rule.
    3. Make a GET request to the rule.
    4. Check that response contains an error.
    5. Check the error.
    """
    parser = lambda rule_type, rule_data: rule_prototype

    def _serializer(*args, **kwargs):
        raise RuleError()

    rule = rule_prototype.create_new(rule_type="RuleError")
    rule_factory.register_rule(rule_type=rule.rule_type, parser=parser, serializer=_serializer)

    rule_id = core_manager.add_rule(rule=rule)

    http_response = application_client.get(rule_endpoint.format(rule_id=rule_id))

    assert http_response.status_code == 500, "Wrong status code"

    message = "Exception has been raised during serialization of the rule"
    assert http_response.json == build_response(error=APIError(message)), "Wrong response"
