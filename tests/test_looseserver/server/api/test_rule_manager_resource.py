"""Test cases for the rule manager resourse of the looseserver API."""

import pytest

from flask import Flask
from flask_restful import Api

from looseserver.common.rule import RuleParseError, RuleError
from looseserver.common.api import APIError
from looseserver.server.api import RulesManager, build_response


# pylint: disable=redefined-outer-name
@pytest.fixture
def rules_manager_endpoint():
    """Endpoint of the rules manager resource."""
    return "/rules"


@pytest.fixture
def application_client(rules_manager_endpoint, core_manager, rule_factory):
    """Client of the configured application."""
    application = Flask("TestApplication")
    api = Api(application)
    api.add_resource(
        RulesManager,
        rules_manager_endpoint,
        resource_class_args=(core_manager, rule_factory),
        )
    return application.test_client()


def test_create_rule(
        core_manager,
        rules_manager_endpoint,
        rule_factory,
        registered_rule_prototype,
        application_client,
    ):
    """Check that rule can be created with API.

    1. Make a POST request to create a rule.
    2. Check that rule is created.
    """
    serialized_rule = rule_factory.serialize_rule(registered_rule_prototype)
    http_response = application_client.post(rules_manager_endpoint, json=serialized_rule)

    assert http_response.status_code == 200, "Wrong status code"

    json_response = http_response.json

    rule_id = json_response["data"].get("rule_id")
    assert rule_id is not None, "Rule ID has not been set"

    expected_data = {"rule_id": rule_id}
    expected_data.update(serialized_rule)

    assert json_response == build_response(data=expected_data), "Wrong response"
    assert core_manager.get_rule(rule_id=rule_id) is not None, "Rule has not been created"


@pytest.mark.parametrize(
    argnames="data",
    argvalues=[None, "Data"],
    ids=["No data", "Not JSON"],
    )
def test_request_data_error(core_manager, rules_manager_endpoint, application_client, data):
    """Check that error is returned if a request does not contain JSON data.

    1. Make a POST request without JSON data.
    2. Check that response contains an error.
    3. Check the error.
    4. Check that rule has not been created.
    """
    http_response = application_client.post(rules_manager_endpoint, data=data)

    assert http_response.status_code == 400, "Wrong status code"

    expected_error = APIError("Failed to parse JSON data from the request")
    assert http_response.json == build_response(error=expected_error), "Wrong response"
    assert not core_manager.get_rules_order(), "Rule has been created"


def test_parse_failed_parse_error(
        core_manager,
        rules_manager_endpoint,
        rule_factory,
        application_client,
    ):
    """Check that error is returned if RuleParseError is raised on attempt to parse data.

    1. Make a POST request without rule type in the data.
    2. Check that response contains an error.
    3. Check the error.
    4. Check that rule has not been created.
    """
    rule_data = {}
    http_response = application_client.post(rules_manager_endpoint, json=rule_data)

    assert http_response.status_code == 400, "Wrong status code"

    parent_error = None
    try:
        rule_factory.parse_rule(data=rule_data)
    except RuleParseError as error:
        parent_error = error

    message = "Failed to create a rule for specified parameters. Error: '{0}'".format(parent_error)
    assert http_response.json == build_response(error=APIError(message)), "Wrong response"
    assert not core_manager.get_rules_order(), "Rule has been created"


def test_parse_failed_unknown_error(
        core_manager,
        rules_manager_endpoint,
        rule_factory,
        rule_prototype,
        application_client,
    ):
    """Check that error is returned if RuleError is raised on attempt to parse data.

    1. Register rule type with parser that raises RuleError.
    2. Make a POST request to create a rule.
    3. Check that response contains an error.
    4. Check the error.
    5. Check that rule has not been created.
    """
    def _parser(*args, **kwargs):
        raise RuleError()

    serializer = lambda rule_type, rule: rule_type

    rule_factory.register_rule(rule_type="RuleError", parser=_parser, serializer=serializer)
    rule = rule_prototype.create_new(rule_type="RuleError")
    serialized_rule = rule_factory.serialize_rule(rule=rule)

    http_response = application_client.post(rules_manager_endpoint, json=serialized_rule)

    assert http_response.status_code == 500, "Wrong status code"

    expected_error = APIError("Exception has been raised during rule creation")
    assert http_response.json == build_response(error=expected_error), "Wrong response"
    assert not core_manager.get_rules_order(), "Rule has been created"


def test_serialization_failed_unknown_error(
        core_manager,
        rules_manager_endpoint,
        rule_factory,
        rule_prototype,
        application_client,
    ):
    """Check that error is returned if RuleError is raised on attempt to serialize a rule.

    1. Register rule type with serializer that raises RuleError.
    2. Make a POST request to create a rule.
    3. Check that response contains an error.
    4. Check the error.
    5. Check that rule has not been created.
    """
    parser = lambda rule_type, rule_data: rule_prototype

    def _serializer(*args, **kwargs):
        raise RuleError()

    rule_factory.register_rule(rule_type="RuleError", parser=parser, serializer=_serializer)

    rule_data = {
        "rule_type": "RuleError",
        "parameters": {}
        }

    http_response = application_client.post(rules_manager_endpoint, json=rule_data)

    assert http_response.status_code == 500, "Wrong status code"

    expected_error = APIError("Rule may be created, but can't be serialized")
    assert http_response.json == build_response(error=expected_error), "Wrong response"
    assert not core_manager.get_rules_order(), "Rule has been created"
