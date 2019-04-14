"""Test cases for the entrypoint."""

import pytest
from flask import Flask

from looseserver.server.application import DEFAULT_BASE_ENDPOINT, DEFAULT_CONFIGURATION_ENDPOINT
import looseserver.default.server.run as run_module
from looseserver.default.client.flask import FlaskClient
from looseserver.default.client.rule import MethodRule
from looseserver.default.client.response import FixedResponse


@pytest.fixture(autouse=True)
def _main(monkeypatch):
    """Fixture to set __name__ of the run module."""
    monkeypatch.setattr(run_module, "__name__", "__main__")


@pytest.fixture(autouse=True)
def flask_run_parameters(monkeypatch):
    """Disable Flask.run method and store its parameters."""
    parameters = {}

    def _patched_run(application, host=None, port=None, debug=None, load_dotenv=True, **options):
        parameters.clear()
        parameters["self"] = application
        parameters["host"] = host
        parameters["port"] = port
        parameters["debug"] = debug
        parameters["load_dotenv"] = load_dotenv
        parameters["options"] = options

    monkeypatch.setattr(Flask, "run", _patched_run)

    return parameters


# pylint: disable=redefined-outer-name
@pytest.mark.parametrize(
    argnames="host,port",
    argvalues=[
        ("localhost", "50000"),
        ("127.0.0.1", "10000"),
        ],
    ids=[
        "Hostname",
        "IP Address",
        ],
    )
def test_run_parameters(flask_run_parameters, host, port):
    """Check that application uses host and port from a commandline.

    1. Run application with host and port parameters in the commandline arguments.
    2. Check that Flask.run method is called with parsed host and port.
    """
    run_module._run(["--host", host, "--port", port])   # pylint: disable=protected-access
    assert flask_run_parameters["host"] == host, "Wrong host"
    assert flask_run_parameters["port"] == int(port), "Wrong port"


@pytest.mark.parametrize(
    argnames="base_endpoint,configuration_endpoint",
    argvalues=[
        (DEFAULT_BASE_ENDPOINT, DEFAULT_CONFIGURATION_ENDPOINT),
        (DEFAULT_BASE_ENDPOINT + "custom/", DEFAULT_CONFIGURATION_ENDPOINT + "custom/"),
        ],
    ids=[
        "Default endpoints",
        "Custom endpoints",
        ],
    )
def test_application(flask_run_parameters, base_endpoint, configuration_endpoint):
    """Check that application is configured with specified endpoints.

    1. Run application with specified base endpoint and configuration endpoint.
    2. Create a flask client with the specified configuration endpoint.
    3. Create a method rule and set a successful response for it.
    4. Make a GET-request for the specified based endpoint.
    5. Check the response.
    """
    commandline_arguments = [
        "--base-endpoint", base_endpoint,
        "--configuration-endpoint", configuration_endpoint,
        ]
    run_module._run(commandline_arguments)  # pylint: disable=protected-access

    application = flask_run_parameters["self"]
    application_client = application.test_client()

    client = FlaskClient(
        configuration_url=configuration_endpoint,
        application_client=application_client,
        )

    rule = client.create_rule(rule=MethodRule(method="GET"))
    client.set_response(rule_id=rule.rule_id, response=FixedResponse(status=200))

    assert application_client.get(base_endpoint).status_code == 200, "Wrong status"
