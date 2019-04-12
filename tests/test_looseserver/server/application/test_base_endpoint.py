"""Test cases for base endpoint."""

from urllib.parse import urljoin

import pytest

from looseserver.server.application import configure_application, DEFAULT_BASE_ENDPOINT


# pylint: disable=redefined-outer-name
@pytest.fixture(params=["", "children", "child/grandchild"], ids=["base", "child", "grandchild"])
def relative_path(request):
    """Relative path."""
    return request.param


@pytest.fixture
def response_setter(
        configuration_endpoint,
        server_rule_factory,
        registered_match_all_rule,
        server_response_factory,
        registered_success_response,
    ):
    """Callable to set a response for an application."""

    def _set_response(application):
        serialized_rule = server_rule_factory.serialize_rule(registered_match_all_rule)

        client = application.test_client()
        http_response = client.post(
            urljoin(configuration_endpoint, "rules"),
            json=serialized_rule,
            )

        rule_id = http_response.json["data"]["rule_id"]

        serialized_response = server_response_factory.serialize_response(
            registered_success_response,
            )

        client.post(
            urljoin(configuration_endpoint, "response/{0}".format(rule_id)),
            json=serialized_response,
            )

    return _set_response


def test_default_routes(
        configuration_endpoint,
        server_rule_factory,
        server_response_factory,
        registered_response_data,
        response_setter,
        relative_path,
    ):
    # pylint: disable=too-many-arguments
    """Check that rules are applied for all nested routes of the default base endpoint.

    1. Configure application without specifying base endpoint.
    2. Set universal response for all routes.
    3. Make a GET-request to one of the nested endpoints.
    4. Check the response.
    """
    application = configure_application(
        configuration_endpoint=configuration_endpoint,
        rule_factory=server_rule_factory,
        response_factory=server_response_factory,
        )

    response_setter(application)

    http_response = application.test_client().get(urljoin(DEFAULT_BASE_ENDPOINT, relative_path))
    assert http_response.status_code == 200
    assert http_response.data == registered_response_data, "Wrong response"


@pytest.mark.parametrize(
    argnames="specified_endpoint,expected_endpoint",
    argvalues=[
        ("/base/", "/base/"),
        ("base/", "/base/"),
        ("/base", "/base/"),
        ],
    ids=[
        "Both slashes",
        "Missing slash at the beginning",
        "Missing slash at the end",
        ],
    )
def test_routes(
        configuration_endpoint,
        server_rule_factory,
        server_response_factory,
        registered_response_data,
        response_setter,
        relative_path,
        specified_endpoint,
        expected_endpoint,
    ):
    # pylint: disable=too-many-arguments
    """Check that rules are applied for all nested routes of the specified base endpoint.

    1. Configure application with specifying base endpoint.
    2. Set universal response for all routes.
    3. Make a GET-request to one of the nested endpoints.
    4. Check the response.
    """
    application = configure_application(
        base_endpoint=specified_endpoint,
        configuration_endpoint=configuration_endpoint,
        rule_factory=server_rule_factory,
        response_factory=server_response_factory,
        )

    response_setter(application)

    http_response = application.test_client().get(urljoin(expected_endpoint, relative_path))
    assert http_response.status_code == 200
    assert http_response.data == registered_response_data, "Wrong response"


def test_unmanaged_routes(
        configuration_endpoint,
        server_rule_factory,
        server_response_factory,
        response_setter,
    ):
    """Check that only paths nested to the default base endpoint are managed.

    1. Configure application without specifying base endpoint.
    2. Set universal response for all routes.
    3. Make a request to the root.
    4. Check that 404 status is returned.
    """
    application = configure_application(
        configuration_endpoint=configuration_endpoint,
        rule_factory=server_rule_factory,
        response_factory=server_response_factory,
        )

    response_setter(application)

    assert application.test_client().get("/").status_code == 404, "Wrong status code"


@pytest.mark.parametrize(
    argnames="method",
    argvalues=["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"],
    )
def test_route_methods(
        configuration_endpoint,
        server_rule_factory,
        server_response_factory,
        response_setter,
        registered_response_data,
        method,
    ):
    # pylint: disable=too-many-arguments
    """Check that all HTTP methods are allowed for the routes.

    1. Configure application without specifying base endpoint.
    2. Set universal response for all routes.
    3. Make a request of the specified type to the base url.
    4. Check the response.
    """
    application = configure_application(
        configuration_endpoint=configuration_endpoint,
        rule_factory=server_rule_factory,
        response_factory=server_response_factory,
        )

    response_setter(application)

    http_response = application.test_client().open(DEFAULT_BASE_ENDPOINT, method=method)
    assert http_response.status_code == 200
    # Response for HEAD-request does not contain a body
    assert http_response.data == registered_response_data or method == "HEAD", "Wrong response"
