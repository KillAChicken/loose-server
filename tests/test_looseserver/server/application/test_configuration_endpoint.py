"""Test cases for configuration endpoint."""

from urllib.parse import urljoin

import pytest

from looseserver.server.application import (
    configure_application,
    DEFAULT_BASE_ENDPOINT,
    DEFAULT_CONFIGURATION_ENDPOINT,
    )


def test_default_configuration_endpoint(
        rule_factory,
        response_factory,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Test the default configuration endpoint of the application.

    1. Configure application without specifying configuration endpoint.
    2. Make a POST request to create a rule (RulesManager resource).
    3. Check the status of the response.
    4. Make a GET request to get the rule (Rule resource).
    5. Check the response.
    6. Make a POST request to set a response for the rule (Response resource).
    7. Check the response.
    8. Make a request to trigger the configured rule and response.
    9. Check the response.
    """
    application = configure_application(
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    rule = server_rule_prototype.create_new(
        rule_type="Test",
        match_implementation=lambda *args, **kwargs: True,
        )

    rule_factory.register_rule(
        rule_type=rule.rule_type,
        parser=lambda *args, **kwargs: rule,
        serializer=lambda *args, **kwargs: {},
        )

    serialized_rule = rule_factory.serialize_rule(rule=rule)

    client = application.test_client()
    http_response = client.post(
        urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "rules"),
        json=serialized_rule,
        )

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]
    http_response = client.get(urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "rule/{0}".format(rule_id)))

    assert http_response.status_code == 200, "Can't obtain the rule"
    assert http_response.json["data"]["rule_id"] == rule_id, "Wrong rule"

    response = server_response_prototype.create_new(
        response_type="Test",
        builder_implementation=lambda *args, **kwargs: b"body",
        )

    response_factory.register_response(
        response_type=response.response_type,
        parser=lambda *args, **kwargs: response,
        serializer=lambda *args, **kwargs: {},
        )

    serialized_response = response_factory.serialize_response(response=response)

    http_response = client.post(
        urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "response/{0}".format(rule_id)),
        json=serialized_response,
        )

    assert http_response.status_code == 200, "Can't set the response"
    assert client.get(DEFAULT_BASE_ENDPOINT).data == b"body", "Wrong response"


@pytest.mark.parametrize(
    argnames="specified_endpoint,expected_endpoint",
    argvalues=[
        ("/config/", "/config/"),
        ("config/", "/config/"),
        ("/config", "/config/"),
        ],
    ids=[
        "Both slashes",
        "Missing slash at the beginning",
        "Missing slash at the end",
        ],
    )
def test_configuration_endpoint(
        rule_factory,
        response_factory,
        server_rule_prototype,
        server_response_prototype,
        specified_endpoint,
        expected_endpoint,
    ):
    # pylint: disable=too-many-arguments
    """Test that specified configuration endpoint is used.

    1. Configure application with specifying configuration endpoint.
    2. Make a POST request to create a rule (RulesManager resource).
    3. Check the status of the response.
    4. Make a GET request to get the rule (Rule resource).
    5. Check the response.
    6. Make a POST request to set a response for the rule (Response resource).
    7. Check the response.
    8. Make a request to trigger the configured rule and response.
    9. Check the response.
    """
    application = configure_application(
        configuration_endpoint=specified_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    rule = server_rule_prototype.create_new(
        rule_type="Test",
        match_implementation=lambda *args, **kwargs: True,
        )

    rule_factory.register_rule(
        rule_type=rule.rule_type,
        parser=lambda *args, **kwargs: rule,
        serializer=lambda *args, **kwargs: {},
        )

    serialized_rule = rule_factory.serialize_rule(rule=rule)

    client = application.test_client()
    http_response = client.post(urljoin(expected_endpoint, "rules"), json=serialized_rule)

    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]
    http_response = client.get(urljoin(expected_endpoint, "rule/{0}".format(rule_id)))

    assert http_response.status_code == 200, "Can't obtain the rule"
    assert http_response.json["data"]["rule_id"] == rule_id, "Wrong rule"

    response = server_response_prototype.create_new(
        response_type="Test",
        builder_implementation=lambda *args, **kwargs: b"body",
        )

    response_factory.register_response(
        response_type=response.response_type,
        parser=lambda *args, **kwargs: response,
        serializer=lambda *args, **kwargs: {},
        )

    serialized_response = response_factory.serialize_response(response=response)

    http_response = client.post(
        urljoin(expected_endpoint, "response/{0}".format(rule_id)),
        json=serialized_response,
        )

    assert http_response.status_code == 200, "Can't set the response"
    assert client.get(DEFAULT_BASE_ENDPOINT).data == b"body", "Wrong response"
