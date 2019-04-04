"""Tests ability to manage rules by the core manager."""

import random

import pytest

import looseserver.server.core as core


def test_add_rule(core_manager, rule_prototype):
    """Check that a rule can be added and obtained.

    1. Add new rule.
    2. Check that rule ID is not None.
    3. Get rule by rule ID.
    4. Check that the same rule has been returned.
    """
    rule_id = core_manager.add_rule(rule=rule_prototype)

    assert rule_id is not None, "Rule ID is None"

    actual_rule = core_manager.get_rule(rule_id=rule_id)
    assert actual_rule is rule_prototype, "Different rule is returned"


def test_add_several_rules(core_manager, rule_prototype):
    """Check that a rule receives new ID.

    1. Add 2 rules.
    2. Check that rule IDs are different.
    3. Check that rules can be obtained by their IDs.
    4. Check order of the rules.
    """
    first_rule = rule_prototype.create_new(rule_type="first")
    first_rule_id = core_manager.add_rule(rule=first_rule)

    second_rule = rule_prototype.create_new(rule_type="second")
    second_rule_id = core_manager.add_rule(rule=second_rule)

    assert first_rule_id is not None, "First rule ID is None"
    assert second_rule_id is not None, "Second rule ID is None"
    assert first_rule_id != second_rule_id, "Rules get the same ID"

    first_actual_rule = core_manager.get_rule(rule_id=first_rule_id)
    assert first_actual_rule is first_rule, "Different rule is returned"

    second_actual_rule = core_manager.get_rule(rule_id=second_rule_id)
    assert second_actual_rule is second_rule, "Different rule is returned"


def test_id_collision(core_manager, rule_prototype, monkeypatch):
    """Check that ID collision is avoided.

    1. Monkeypatch uuid function to return the same ID several times.
    2. Create a rule.
    3. Create another rule.
    4. Check that rules have different IDs.
    """
    ids = iter(("1", "1", "1", "2"))
    def _patched_uuid4(*args, **kwargs):
        # pylint: disable=unused-argument
        return next(ids)

    monkeypatch.setattr(core, "uuid4", _patched_uuid4)

    first_rule_id = core_manager.add_rule(rule_prototype)
    second_rule_id = core_manager.add_rule(rule_prototype)

    assert first_rule_id == "1", "Wrong rule ID"
    assert second_rule_id == "2", "Wrong rule ID"


def test_get_non_existent_rule(core_manager, rule_prototype):
    """Check that KeyError is raised if rule does not exist.

    1. Create a rule.
    2. Try to get rule with fake ID.
    3. Check that KeyError is raised.
    4. Check the message of the error.
    """
    core_manager.add_rule(rule=rule_prototype)
    with pytest.raises(KeyError) as exception_info:
        core_manager.get_rule("FakeID")

    assert exception_info.value.args[0] == "Failed to find a rule with ID: 'FakeID'", (
        "Wrong error message"
        )


@pytest.mark.parametrize(
    argnames="rule_index",
    argvalues=[0, 1, -1],
    ids=["First", "Middle", "Last"],
    )
def remove_rule(core_manager, rule_prototype, rule_index):
    """Check that a rule can be removed.

    1. Create 3 rules.
    2. Remove a rule.
    3. Check that the rule is removed.
    """
    rule_ids = [core_manager.add_rule(rule=rule_prototype) for _ in range(3)]
    rule_id_to_remove = rule_ids[rule_index]
    core_manager.remove_rule(rule_id=rule_id_to_remove)

    with pytest.raises(KeyError):
        core_manager.get_rule(rule_id=rule_id_to_remove)


@pytest.mark.parametrize(
    argnames="number_of_rules",
    argvalues=[0, 1, 3],
    ids=["No rules", "Single rule", "Several rules"],
    )
def test_rules_order_after_add(core_manager, rule_prototype, number_of_rules):
    """Check order of the rules after rule's being added.

    1. Create several rules.
    2. Check order of the rules.
    """
    rule_ids = tuple(core_manager.add_rule(rule=rule_prototype) for _ in range(number_of_rules))
    rules_order = core_manager.get_rules_order()
    assert rules_order == rule_ids, "Wrong order of rules"


@pytest.mark.parametrize(
    argnames="number_of_rules",
    argvalues=[0, 1, 2],
    ids=["No rules left", "Single rule left", "Several rules left"],
    )
def test_rules_order_after_remove(core_manager, rule_prototype, number_of_rules):
    """Check order of the rules after rule's being removed.

    1. Create several rules.
    2. Remove one of the rules.
    3. Check order of the rules.
    """
    rule_ids = [core_manager.add_rule(rule=rule_prototype) for _ in range(number_of_rules + 1)]
    rule_id_to_remove = random.choice(rule_ids)

    core_manager.remove_rule(rule_id_to_remove)

    rule_ids.remove(rule_id_to_remove)

    rules_order = core_manager.get_rules_order()
    assert rules_order == tuple(rule_ids), "Wrong order of rules"
