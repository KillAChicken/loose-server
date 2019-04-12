"""Configuration of pytest."""

from urllib.parse import urljoin

import pytest


# pylint: disable=redefined-outer-name
@pytest.fixture
def rule_match_all(server_rule_factory, server_rule_prototype):
    """Registered rule that matches every request."""
    rule = server_rule_prototype.create_new(
        rule_type="MATCHALL",
        match_implementation=lambda *args, **kwargs: True,
        )

    server_rule_factory.register_rule(
        rule_type=rule.rule_type,
        parser=lambda *args, **kwargs: rule,
        serializer=lambda *args, **kwargs: {},
        )

    return rule


@pytest.fixture
def apply_response(
        configuration_endpoint,
        server_rule_factory,
        server_response_factory,
        configured_application_client,
        rule_match_all,
    ):
    """Callable that creates an universal rule and sets a specified response for it."""
    def _apply_response(response):
        serialized_rule = server_rule_factory.serialize_rule(rule=rule_match_all)

        http_response = configured_application_client.post(
            urljoin(configuration_endpoint, "rules"),
            json=serialized_rule,
            )
        assert http_response.status_code == 200, "Can't create a rule"

        rule_id = http_response.json["data"]["rule_id"]

        serialized_response = server_response_factory.serialize_response(response=response)

        http_response = configured_application_client.post(
            urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
            json=serialized_response,
            )
        assert http_response.status_code == 200, "Can't set a response"

    return _apply_response
# pylint: enable=redefined-outer-name
