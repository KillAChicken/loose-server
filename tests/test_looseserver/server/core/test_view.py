"""Tests for the view provided by the core manager."""


def test_view(
        base_endpoint,
        core_manager,
        managed_application_client,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check configured response.

    1. Create a rule that is triggered for every endpoint.
    2. Set response.
    3. Make a request.
    4. Check that the configured response was returned.
    """
    rule = server_rule_prototype.create_new(match_implementation=lambda *args, **kwargs: True)

    response = server_response_prototype.create_new(
        builder_implementation=lambda *args, **kwargs: b"test body"
        )

    rule_id = core_manager.add_rule(rule)
    core_manager.set_response(rule_id=rule_id, response=response)

    http_response = managed_application_client.get(base_endpoint)

    assert http_response.status_code == 200, "Wrong status code"
    assert http_response.data == b"test body", "Wrong body"


def test_reset_response(
        base_endpoint,
        core_manager,
        managed_application_client,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check that response for a rule can be changed.

    1. Create a rule, that is triggered for every endpoint.
    2. Set a response.
    3. Set another response for the same rule.
    4. Make a request.
    5. Check that new response is returned.
    """
    rule = server_rule_prototype.create_new(match_implementation=lambda *args, **kwargs: True)
    rule_id = core_manager.add_rule(rule=rule)

    initial_implementation_triggered = False
    def _initial_builder_implementation(*args, **kwargs):
        # pylint: disable=unused-argument
        nonlocal initial_implementation_triggered
        initial_implementation_triggered = True
        return b"First response"

    first_response = server_response_prototype.create_new(
        builder_implementation=_initial_builder_implementation,
        )

    core_manager.set_response(rule_id=rule_id, response=first_response)

    second_response = server_response_prototype.create_new(
        builder_implementation=lambda *args, **kwargs: b"Second response",
        )

    core_manager.set_response(rule_id=rule_id, response=second_response)

    http_response = managed_application_client.get(base_endpoint)

    assert not initial_implementation_triggered, "Initial response was triggered"
    assert http_response.status_code == 200, "Wrong status code"
    assert http_response.data == b"Second response", "Wrong body"


def test_second_rule(
        base_endpoint,
        core_manager,
        managed_application_client,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check that rule can be triggered if no match has been found by other rules.

    1. Create a rule, that does not find match for any request.
    2. Create a rule, that is triggered for every request.
    3. Create different responses for the rules.
    4. Make a request.
    5. Check that response for the second rule is returned.
    """
    implementation_triggered = False
    def _no_match_implementation(*args, **kwargs):
        # pylint: disable=unused-argument
        nonlocal implementation_triggered
        implementation_triggered = True
        return False

    no_match_rule = server_rule_prototype.create_new(match_implementation=_no_match_implementation)
    no_match_rule_id = core_manager.add_rule(rule=no_match_rule)

    match_rule = server_rule_prototype.create_new(match_implementation=lambda *args, **kwargs: True)
    match_rule_id = core_manager.add_rule(rule=match_rule)

    no_match_response = server_response_prototype.create_new(
        builder_implementation=lambda *args, **kwargs: b"No match response",
        )
    core_manager.set_response(rule_id=no_match_rule_id, response=no_match_response)

    match_response = server_response_prototype.create_new(
        builder_implementation=lambda *args, **kwargs: b"Match response",
        )
    core_manager.set_response(rule_id=match_rule_id, response=match_response)

    http_response = managed_application_client.get(base_endpoint)

    assert implementation_triggered, "First rule was not checked"
    assert http_response.status_code == 200, "Wrong status code"
    assert http_response.data == b"Match response", "Wrong body"


def test_no_rules(base_endpoint, managed_application_client):
    """Check that 404 status is returned if no rule is configured.

    1. Make a request to a route.
    2. Check that 404 status is returned.
    """
    http_response = managed_application_client.get(base_endpoint)
    assert http_response.status_code == 404, "Wrong response status"


def test_no_matching_rule(
        base_endpoint,
        core_manager,
        managed_application_client,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check that 404 status is returned if there is no rule matching the request.

    1. Create a rule, matching no requests.
    2. Set response for the rule.
    3. Make a request.
    4. Check that 404 status is returned.
    """
    rule = server_rule_prototype.create_new(match_implementation=lambda *args, **kwargs: False)
    rule_id = core_manager.add_rule(rule=rule)

    response = server_response_prototype.create_new(
        builder_implementation=lambda *args, **kwargs: b"",
        )
    core_manager.set_response(rule_id=rule_id, response=response)

    http_response = managed_application_client.get(base_endpoint)
    assert http_response.status_code == 404, "Wrong response status"


def test_no_response(
        base_endpoint,
        core_manager,
        managed_application_client,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check that rule is skipped if no response is configured for it.

    1. Create 2 rules, matching every request.
    2. Set response only for the second rule.
    3. Make a request.
    4. Check that response is succesfully obtained.
    """
    rule = server_rule_prototype.create_new(match_implementation=lambda *args, **kwargs: True)
    core_manager.add_rule(rule=rule)
    second_rule_id = core_manager.add_rule(rule=rule)

    response = server_response_prototype.create_new(
        builder_implementation=lambda *args, **kwargs: b"Response",
        )
    core_manager.set_response(rule_id=second_rule_id, response=response)

    http_response = managed_application_client.get(base_endpoint)

    assert http_response.status_code == 200, "Wrong status code"
    assert http_response.data == b"Response", "Wrong body"


def test_exception_in_matching(
        base_endpoint,
        core_manager,
        managed_application_client,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check that rule is skipped if exception is raised on attempt to match.

    1. Create a rule, raising an exception on attempt to find a match.
    2. Create a rule, that matches every request.
    3. Set different responses for both rules.
    4. Make a request.
    5. Check that response, build for the second rule, is returned.
    """
    implementation_triggered = False
    def _exceptional_match_implementation(*args, **kwargs):
        # pylint: disable=unused-argument
        nonlocal implementation_triggered
        implementation_triggered = True
        raise NotImplementedError()

    exceptional_rule = server_rule_prototype.create_new(
        match_implementation=_exceptional_match_implementation,
        )
    exceptional_rule_id = core_manager.add_rule(rule=exceptional_rule)

    successful_rule = server_rule_prototype.create_new(
        match_implementation=lambda *args, **kwargs: True,
        )
    successful_rule_id = core_manager.add_rule(rule=successful_rule)

    first_response = server_response_prototype.create_new(
        builder_implementation=lambda *args, **kwargs: b"First response"
        )
    core_manager.set_response(rule_id=exceptional_rule_id, response=first_response)

    second_response = server_response_prototype.create_new(
        builder_implementation=lambda *args, **kwargs: b"Second response"
        )
    core_manager.set_response(rule_id=successful_rule_id, response=second_response)

    http_response = managed_application_client.get(base_endpoint)

    assert implementation_triggered, "Exceptional rule was not triggered"
    assert http_response.status_code == 200, "Wrong status code"
    assert http_response.data == b"Second response", "Wrong body"


def test_exception_in_response_building(
        base_endpoint,
        core_manager,
        managed_application_client,
        server_rule_prototype,
        server_response_prototype,
    ):
    """Check that rule is skipped if exception is raised while building a response.

    1. Create 2 rules, matching every request.
    2. Set response for the first rule, raising an exception.
    3. Set response for the second rule.
    4. Make a request.
    5. Check that response, build for the second rule, is returned.
    """
    rule = server_rule_prototype.create_new(match_implementation=lambda *args, **kwargs: True)
    exceptional_rule_id = core_manager.add_rule(rule=rule)
    successful_rule_id = core_manager.add_rule(rule=rule)

    implementation_triggered = False
    def _exceptional_builder_implementation(*args, **kwargs):
        # pylint: disable=unused-argument
        nonlocal implementation_triggered
        implementation_triggered = True
        raise NotImplementedError()

    exceptional_response = server_response_prototype.create_new(
        builder_implementation=_exceptional_builder_implementation,
        )

    core_manager.set_response(rule_id=exceptional_rule_id, response=exceptional_response)

    successful_builder_implementation = lambda *args, **kwargs: b"Successful response"
    successful_response = server_response_prototype.create_new(
        builder_implementation=successful_builder_implementation,
        )

    core_manager.set_response(rule_id=successful_rule_id, response=successful_response)

    http_response = managed_application_client.get(base_endpoint)

    assert implementation_triggered, "Exceptional response was not triggered"
    assert http_response.status_code == 200, "Wrong status code"
    assert http_response.data == b"Successful response", "Wrong body"
