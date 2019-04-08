"""Test cases for the response resourse of the looseserver API."""

import pytest

from flask import Flask
from flask_restful import Api

from looseserver.common.response import ResponseParseError, ResponseError
from looseserver.common.api import APIError
from looseserver.server.api import Response, build_response


# pylint: disable=redefined-outer-name
@pytest.fixture
def response_endpoint():
    """Endpoint of the rules manager resource."""
    return "/rule/{rule_id}"


@pytest.fixture
def application_client(response_endpoint, core_manager, response_factory):
    """Client of the configured application."""
    application = Flask("TestApplication")
    api = Api(application)
    api.add_resource(
        Response,
        response_endpoint.format(rule_id="<rule_id>"),
        resource_class_args=(core_manager, response_factory),
        )
    return application.test_client()


def test_set_response(
        core_manager,
        response_endpoint,
        response_factory,
        server_rule_prototype,
        registered_response_prototype,
        application_client,
    ):
    # pylint: disable=too-many-arguments
    """Check that response can be set with API.

    1. Create a rule.
    2. Make a POST request to set a response for the rule.
    3. Check that response is set.
    """
    rule_id = core_manager.add_rule(server_rule_prototype)

    serialized_response = response_factory.serialize_response(registered_response_prototype)
    http_response = application_client.post(
        response_endpoint.format(rule_id=rule_id),
        json=serialized_response,
        )

    assert http_response.status_code == 200, "Wrong status code"
    assert http_response.json == build_response(data=serialized_response), "Wrong response"
    assert core_manager.get_response(rule_id=rule_id) is not None, "Response has not been set"


@pytest.mark.parametrize(
    argnames="data",
    argvalues=[None, "Data"],
    ids=["No data", "Not JSON"],
    )
def test_request_data_error(
        core_manager,
        response_endpoint,
        server_rule_prototype,
        application_client,
        data,
    ):
    """Check that error is returned if a request does not contain JSON data.

    1. Create a rule.
    2. Make a POST request to set response without JSON data.
    3. Check that response contains an error.
    4. Check the error.
    5. Check that response has not been set.
    """
    rule_id = core_manager.add_rule(server_rule_prototype)

    http_response = application_client.post(
        response_endpoint.format(rule_id=rule_id),
        data=data,
        )

    assert http_response.status_code == 400, "Wrong status code"

    expected_error = APIError("Failed to parse JSON data from the request")
    assert http_response.json == build_response(error=expected_error), "Wrong response"

    with pytest.raises(KeyError):
        core_manager.get_response(rule_id=rule_id)


def test_parse_failed_parse_error(
        core_manager,
        response_endpoint,
        response_factory,
        server_rule_prototype,
        application_client,
    ):
    """Check that error is returned if ResponseParseError is raised on attempt to parse data.

    1. Create a rule.
    2. Make a POST request to set resonse without response type in the data.
    3. Check that response contains an error.
    4. Check the error.
    5. Check that response has not been set.
    """
    rule_id = core_manager.add_rule(server_rule_prototype)

    response_data = {}
    http_response = application_client.post(
        response_endpoint.format(rule_id=rule_id),
        json=response_data,
        )

    assert http_response.status_code == 400, "Wrong status code"

    parent_error = None
    try:
        response_factory.parse_response(data=response_data)
    except ResponseParseError as error:
        parent_error = error

    message = "Failed to create a response for specified parameters. Error: '{0}'".format(
        parent_error,
        )
    assert http_response.json == build_response(error=APIError(message)), "Wrong response"

    with pytest.raises(KeyError):
        core_manager.get_response(rule_id=rule_id)


def test_parse_failed_unknown_error(
        core_manager,
        response_endpoint,
        response_factory,
        server_rule_prototype,
        server_response_prototype,
        application_client,
    ):
    # pylint: disable=too-many-arguments
    """Check that error is returned if ResponseError is raised on attempt to parse data.

    1. Create a rule.
    2. Register response type with parser that raises ResponseError.
    3. Make a POST request to set a response.
    4. Check that response contains an error.
    5. Check the error.
    6. Check that response has not been set.
    """
    rule_id = core_manager.add_rule(server_rule_prototype)

    def _parser(*args, **kwargs):
        raise ResponseError()

    serializer = lambda response_type, response: response_type

    response = server_response_prototype.create_new(response_type="RuleError")
    response_factory.register_response(
        response_type=response.response_type,
        parser=_parser,
        serializer=serializer,
        )
    serialized_response = response_factory.serialize_response(response=response)

    http_response = application_client.post(
        response_endpoint.format(rule_id=rule_id),
        json=serialized_response,
        )

    assert http_response.status_code == 500, "Wrong status code"

    expected_error = APIError("Exception has been raised during response creation")
    assert http_response.json == build_response(error=expected_error), "Wrong response"

    with pytest.raises(KeyError):
        core_manager.get_response(rule_id=rule_id)


def test_set_response_serialization_failed(
        core_manager,
        response_endpoint,
        response_factory,
        server_rule_prototype,
        server_response_prototype,
        application_client,
    ):
    # pylint: disable=too-many-arguments
    """Check that error is returned if ResponseError is raised on attempt to serialize a rule.

    1. Create a rule.
    2. Register response type with serializer that raises ResponseError.
    3. Make a POST request to set a response.
    4. Check that response contains an error.
    5. Check the error.
    6. Check that response has not been set.
    """
    rule_id = core_manager.add_rule(server_rule_prototype)

    parser = lambda response_type, response_data: server_response_prototype

    def _serializer(*args, **kwargs):
        raise ResponseError()

    response_factory.register_response(
        response_type="ResponseError",
        parser=parser,
        serializer=_serializer,
        )

    response_data = {
        "response_type": "ResponseError",
        "parameters": {}
        }

    http_response = application_client.post(
        response_endpoint.format(rule_id=rule_id),
        json=response_data,
        )

    assert http_response.status_code == 500, "Wrong status code"

    expected_error = APIError("Response can't be serialized")
    assert http_response.json == build_response(error=expected_error), "Wrong response"

    with pytest.raises(KeyError):
        core_manager.get_response(rule_id=rule_id)


def test_set_response_non_existent_rule(
        core_manager,
        response_endpoint,
        response_factory,
        server_rule_prototype,
        registered_response_prototype,
        application_client,
    ):
    # pylint: disable=too-many-arguments
    """Check that error is returned on attempt to set response for a non-existent rule.

    1. Create a rule.
    2. Make a POST request to set a response for a not-existent rule.
    3. Check that response contains an error.
    4. Check the error.
    """
    core_manager.add_rule(server_rule_prototype)

    serialized_response = response_factory.serialize_response(registered_response_prototype)
    http_response = application_client.post(
        response_endpoint.format(rule_id="FakeID"),
        json=serialized_response,
        )

    assert http_response.status_code == 400, "Wrong status code"

    expected_error = APIError("Failed to create a response: Rule does not exist")
    assert http_response.json == build_response(error=expected_error), "Wrong response"


def test_get_response(
        core_manager,
        response_endpoint,
        response_factory,
        server_rule_prototype,
        registered_response_prototype,
        application_client,
    ):
    # pylint: disable=too-many-arguments
    """Check that response can be obtained with API.

    1. Create a rule.
    2. Set a response for the rule.
    2. Make a GET request to get a response.
    3. Check that response is obtained.
    """
    rule_id = core_manager.add_rule(server_rule_prototype)
    core_manager.set_response(rule_id=rule_id, response=registered_response_prototype)

    http_response = application_client.get(response_endpoint.format(rule_id=rule_id))
    assert http_response.status_code == 200, "Wrong status code"

    expected_data = response_factory.serialize_response(registered_response_prototype)
    assert http_response.json == build_response(data=expected_data), "Wrong response"


def test_get_response_non_existent_rule(
        core_manager,
        response_endpoint,
        server_rule_prototype,
        application_client,
    ):
    """Check that error is returned on attempt to get response for a non-existent rule.

    1. Create a rule.
    2. Make a GET request to get a response for a not-existent rule.
    3. Check that response contains an error.
    4. Check the error.
    """
    core_manager.add_rule(server_rule_prototype)

    http_response = application_client.get(response_endpoint.format(rule_id="FakeID"))

    assert http_response.status_code == 404, "Wrong status code"

    message = "Failed to get response for the rule 'FakeID'"
    assert http_response.json == build_response(error=APIError(message)), "Wrong response"


def test_get_response_serialization_failed(
        core_manager,
        response_endpoint,
        response_factory,
        server_rule_prototype,
        server_response_prototype,
        application_client,
    ):
    # pylint: disable=too-many-arguments
    """Check that error is returned if ResponseError is raised on attempt to serialize a rule.

    1. Create a rule.
    2. Register response type with serializer that raises ResponseError.
    3. Set response for the rule.
    4. Make a GET request to get a response.
    5. Check that response contains an error.
    6. Check the error.
    """
    rule_id = core_manager.add_rule(server_rule_prototype)
    response = server_response_prototype.create_new(response_type="ResponseError")
    core_manager.set_response(rule_id=rule_id, response=response)

    parser = lambda response_type, response_data: server_response_prototype

    def _serializer(*args, **kwargs):
        raise ResponseError()

    response_factory.register_response(
        response_type=response.response_type,
        parser=parser,
        serializer=_serializer,
        )

    http_response = application_client.get(response_endpoint.format(rule_id=rule_id))

    assert http_response.status_code == 500, "Wrong status code"

    expected_error = APIError("Response can't be serialized")
    assert http_response.json == build_response(error=expected_error), "Wrong response"
