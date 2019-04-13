"""Test cases for creation of the default rule factory."""

from urllib.parse import urljoin

from looseserver.server.application import DEFAULT_BASE_ENDPOINT
from looseserver.client.flask import FlaskClient
from looseserver.default.client.rule import create_rule_factory, PathRule, MethodRule, CompositeRule


def test_create_rule_factory(
        base_endpoint,
        configuration_endpoint,
        client_response_factory,
        default_factories_application,
    ):
    """Check that default rules are registered in the default rule factory.

    1. Configure application with default rule factory.
    2. Create default rule factory for client.
    3. Create a path, method and composite rules with the client.
    4. Check that responses are successful.
    """
    rule_factory = create_rule_factory(base_url=base_endpoint)

    client = FlaskClient(
        configuration_url=configuration_endpoint,
        rule_factory=rule_factory,
        response_factory=client_response_factory,
        application_client=default_factories_application.test_client(),
        )

    path_rule_spec = PathRule(path="path")
    path_rule = client.create_rule(rule=path_rule_spec)
    assert path_rule.rule_id is not None, "Rule was not created"

    method_rule_spec = MethodRule(method="DELETE")
    method_rule = client.create_rule(rule=method_rule_spec)
    assert method_rule.rule_id is not None, "Rule was not created"

    composite_rule_spec = CompositeRule(children=[path_rule_spec, method_rule_spec])
    composite_rule = client.create_rule(rule=composite_rule_spec)
    assert composite_rule.rule_id is not None, "Rule was not created"


def test_base_url():
    """Check that default path rule is configured with the specified base url.

    1. Create default rule factory with specified base url.
    2. Serialize a path rule with relative path.
    3. Parse serialized rule.
    4. Check the path of the parsed rule.
    """
    base_url = "/base/"
    rule_factory = create_rule_factory(base_url=base_url)

    rule = PathRule(path="path")
    serialized_rule = rule_factory.serialize_rule(rule=rule)
    parsed_rule = rule_factory.parse_rule(data=serialized_rule)

    assert parsed_rule.path == urljoin(base_url, rule.path), "Wrong path"


def test_default_base_url():
    """Check that default path rule is configured with the default base url if None was specified.

    1. Create default rule factory without specifying base url.
    2. Serialize a path rule with relative path.
    3. Parse serialized rule.
    4. Check the path of the parsed rule.
    """
    rule_factory = create_rule_factory()

    rule = PathRule(path="path")
    serialized_rule = rule_factory.serialize_rule(rule=rule)
    parsed_rule = rule_factory.parse_rule(data=serialized_rule)

    assert parsed_rule.path == urljoin(DEFAULT_BASE_ENDPOINT, rule.path), "Wrong path"
