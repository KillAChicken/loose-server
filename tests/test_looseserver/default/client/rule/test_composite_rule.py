"""Test cases for CompositeRule."""

import random

import pytest

from looseserver.default.common.constants import RuleType
from looseserver.default.common.configuration import RuleFactoryPreparator
from looseserver.default.client.rule import MethodRule, CompositeRule


# pylint: disable=redefined-outer-name
@pytest.fixture(params=[2, 1, 0], ids=["Several children", "Single child", "No children"])
def children(request):
    """Children of the composite rule."""
    methods = ["GET", "HEAD", "POST", "PUT", "DELETE", "OPTIONS", "CONNECT", "TRACE", "PATCH"]
    return [MethodRule(method=random.choice(methods)) for _ in range(request.param)]


def test_default_rule_type():
    """Check the default rule type of the composite rule.

    1. Create a composite rule without specifying its type.
    2. Check the rule type.
    """
    rule = CompositeRule(children=())
    assert rule.rule_type == RuleType.COMPOSITE.name, "Wrong rule type"


def test_rule_representation(children):
    """Check the representation of the composite rule.

    1. Create a composite rule.
    2. Check result of the repr function.
    """
    rule = CompositeRule(children=children)
    assert repr(rule) == "CompositeRule(children={0})".format(tuple(children)), (
        "Wrong representation"
        )


def test_creation(configured_flask_client, client_rule_factory, children):
    """Check that CompositeRule can be created.

    1. Prepare composite rule in the rule factory of the flask client.
    2. Create a composite rule with the client.
    3. Check the created rule.
    """
    preparator = RuleFactoryPreparator(client_rule_factory)
    preparator.prepare_method_rule(method_rule_class=MethodRule)
    preparator.prepare_composite_rule(composite_rule_class=CompositeRule)

    rule_spec = CompositeRule(children=children)
    rule = configured_flask_client.create_rule(rule=rule_spec)

    assert rule.rule_id is not None, "Rule was not created"
    assert len(rule_spec.children) == len(children), "Wrong number of children"
