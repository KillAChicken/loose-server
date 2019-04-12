"""Configuration of pytest."""

from urllib.parse import urljoin

import pytest


@pytest.fixture
def apply_rule(
        configuration_endpoint,
        server_rule_factory,
        server_response_factory,
        configured_application_client,
        server_response_prototype,
    ):
    """Callable that creates a specified rule and sets successful response for it."""
    response = server_response_prototype.create_new(
        response_type="RESPONSE200",
        builder_implementation=lambda *args, **kwargs: b""
        )

    server_response_factory.register_response(
        response_type=response.response_type,
        parser=lambda *args, **kwargs: response,
        serializer=lambda *args, **kwargs: {},
        )

    def _apply_rule(rule):
        serialized_rule = server_rule_factory.serialize_rule(rule=rule)

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

    return _apply_rule
