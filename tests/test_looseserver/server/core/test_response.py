"""Tests ability to manage responses by the core manager."""

import pytest


def test_set_response(core_manager, server_rule_prototype, server_response_prototype):
    """Check that response can be set for a rule.

    1. Add new rule.
    2. Set response.
    3. Get response of the rule.
    4. Check that the same response has been returned.
    """
    rule_id = core_manager.add_rule(rule=server_rule_prototype)
    core_manager.set_response(rule_id=rule_id, response=server_response_prototype)

    actual_response = core_manager.get_response(rule_id=rule_id)
    assert actual_response is server_response_prototype, "Different response has been returned"


def test_set_response_several_rules(core_manager, server_rule_prototype, server_response_prototype):
    """Check that response can be set for several rules.

    1. Add 2 rules.
    2. Set different responses for the rules.
    3. Get responses of the rules.
    4. Check that correct responses have been returned.
    """
    first_rule_id = core_manager.add_rule(rule=server_rule_prototype.create_new())
    second_rule_id = core_manager.add_rule(rule=server_rule_prototype.create_new())

    first_response = server_response_prototype.create_new(response_type="first")
    second_response = server_response_prototype.create_new(response_type="second")

    core_manager.set_response(rule_id=first_rule_id, response=first_response)
    core_manager.set_response(rule_id=second_rule_id, response=second_response)

    first_actual_response = core_manager.get_response(rule_id=first_rule_id)
    assert first_actual_response is first_response, "Different resonse has been returned"

    second_actual_response = core_manager.get_response(rule_id=second_rule_id)
    assert second_actual_response is second_response, "Different resonse has been returned"


def test_set_response_non_existent_rule(
        core_manager,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check that KeyError is raised on attempt to set response for non-existent rule.

    1. Create a rule.
    2. Set response for the rule.
    3. Try to set response for a non-existent rule.
    4. Check that KeyError is raised.
    5. Check the message of the error.
    """
    rule_id = core_manager.add_rule(rule=server_rule_prototype)
    core_manager.set_response(rule_id=rule_id, response=server_response_prototype)
    with pytest.raises(KeyError) as exception_info:
        core_manager.set_response(rule_id="FakeID", response=server_response_prototype)

    assert exception_info.value.args[0] == "Failed to find a rule with ID: 'FakeID'", (
        "Wrong error message"
        )


def test_set_response_removed_rule(core_manager, server_rule_prototype, server_response_prototype):
    """Check that KeyError is raised on attempt to set response for non-existent rule.

    1. Create a rule.
    2. Set response for the rule.
    3. Remove the rule.
    4. Try to set response for the removed rule.
    5. Check that KeyError is raised.
    6. Check the message of the error.
    """
    rule_id = core_manager.add_rule(rule=server_rule_prototype)
    core_manager.set_response(rule_id=rule_id, response=server_response_prototype)
    core_manager.remove_rule(rule_id=rule_id)
    with pytest.raises(KeyError) as exception_info:
        core_manager.set_response(rule_id=rule_id, response=server_response_prototype)

    message = "Failed to find a rule with ID: '{0}'".format(rule_id)
    assert exception_info.value.args[0] == message, "Wrong error message"


def test_get_response_non_existent_rule(
        core_manager,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check that KeyError is raised on attempt to set response for non-existent rule.

    1. Create a rule.
    2. Set response for the rule.
    3. Try to get response of a non-existent rule.
    4. Check that KeyError is raised.
    5. Check the message of the error.
    """
    rule_id = core_manager.add_rule(rule=server_rule_prototype)
    core_manager.set_response(rule_id=rule_id, response=server_response_prototype)
    with pytest.raises(KeyError) as exception_info:
        core_manager.get_response(rule_id="FakeID")

    assert exception_info.value.args[0] == "Failed to find a rule with ID: 'FakeID'", (
        "Wrong error message"
        )


def test_get_response_removed_rule(core_manager, server_rule_prototype, server_response_prototype):
    """Check that KeyError is raised on attempt to set response for removed rule.

    1. Create a rule.
    2. Set response for the rule.
    3. Remove the rule.
    4. Try to get response of the removed rule.
    5. Check that KeyError is raised.
    6. Check the message of the error.
    """
    rule_id = core_manager.add_rule(rule=server_rule_prototype)
    core_manager.set_response(rule_id=rule_id, response=server_response_prototype)
    core_manager.remove_rule(rule_id)

    with pytest.raises(KeyError) as exception_info:
        core_manager.get_response(rule_id=rule_id)

    message = "Failed to find a rule with ID: '{0}'".format(rule_id)
    assert exception_info.value.args[0] == message, "Wrong error message"


def test_get_empty_response(core_manager, server_rule_prototype, server_response_prototype):
    """Check that KeyError is raised on attempt to get response of the rule without response.

    1. Create 2 rules.
    2. Set response for the first rule.
    3. Try to get response of the second rule.
    4. Check that KeyError is raised.
    5. Check the message of the error.
    """
    first_rule_id = core_manager.add_rule(rule=server_rule_prototype)
    second_rule_id = core_manager.add_rule(rule=server_rule_prototype)

    core_manager.set_response(rule_id=first_rule_id, response=server_response_prototype)
    with pytest.raises(KeyError) as exception_info:
        core_manager.get_response(rule_id=second_rule_id)

    expected_message = "Response has not been set for the rule with ID: '{0}'".format(
        second_rule_id,
        )
    assert exception_info.value.args[0] == expected_message, "Wrong error message"
