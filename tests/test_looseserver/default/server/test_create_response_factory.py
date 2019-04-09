"""Test cases for creation of the default response factory."""

from urllib.parse import urljoin

from looseserver.server.application import configure_application
from looseserver.default.common.constants import ResponseType
from looseserver.default.server.response import create_response_factory, FixedResponse


def test_create_response_factory(rule_factory, rule_match_all):
    """Check that default responses are registered in the default response factory.

    1. Create default response factory.
    2. Configure application with the response factory.
    3. Create a rule.
    4. Make a POST-request to set a fixed response for the rule.
    5. Check that responses are successful.
    """
    configuration_endpoint = "/config/"

    response_factory = create_response_factory()

    application = configure_application(
        configuration_endpoint=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=response_factory,
        )

    client = application.test_client()

    serialized_rule = rule_factory.serialize_rule(rule=rule_match_all)
    http_response = client.post(urljoin(configuration_endpoint, "rules"), json=serialized_rule)
    assert http_response.status_code == 200, "Can't create a rule"

    rule_id = http_response.json["data"]["rule_id"]

    fixed_response = FixedResponse(
        response_type=ResponseType.FIXED.name,
        status=200,
        headers={},
        body="",
        )
    serialized_fixed_response = response_factory.serialize_response(response=fixed_response)

    fixed_response_response = client.post(
        urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
        json=serialized_fixed_response,
        )
    assert fixed_response_response.status_code == 200, "Can't set a response"
