"""Test cases for PathRule."""

from urllib.parse import urljoin

from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator
from looseserver.default.client.rule import PathRule
from looseserver.server.application import configure_application
from looseserver.client.flask import FlaskClient


def test_default_rule_type():
    """Check the default rule type of the path rule.

    1. Create a path rule without specifying its type.
    2. Check the rule type.
    """
    rule = PathRule(path="path")
    assert rule.rule_type == RuleType.PATH.name, "Wrong rule type"


def test_rule_representation():
    """Check the representation of the path rule.

    1. Create a path rule.
    2. Check result of the repr function.
    """
    rule = PathRule(path="test")
    assert repr(rule) == "PathRule(path='test')", "Wrong representation"


def test_creation(base_endpoint, configuration_endpoint, rule_factory):
    """Check that PathRule can be created.

    1. Configure application with default rule factory.
    2. Prepare path rule in the rule factory of the flask client.
    3. Create a path rule with the client.
    4. Check the created rule.
    """
    application = configure_application(
        base_endpoint=base_endpoint,
        configuration_endpoint=configuration_endpoint,
        )

    preparator = RuleFactoryPreparator(rule_factory)
    preparator.prepare_path_rule(path_rule_class=PathRule, base_url=base_endpoint)

    client = FlaskClient(
        base_url=configuration_endpoint,
        rule_factory=rule_factory,
        application_client=application.test_client(),
        )

    rule_spec = PathRule(path="path-rule")
    rule = client.create_rule(rule=rule_spec)

    assert rule.rule_id is not None, "Rule was not created"
    assert rule.path == urljoin(base_endpoint, rule_spec.path), "Wrong path"
