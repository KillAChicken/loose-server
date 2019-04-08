"""Test cases for base endpoint."""

from urllib.parse import urljoin

import pytest

from looseserver.server.application import (
    configure_application,
    DEFAULT_BASE_ENDPOINT,
    DEFAULT_CONFIGURATION_ENDPOINT,
    )


# pylint: disable=redefined-outer-name
@pytest.fixture(params=["", "children", "child/grandchild"], ids=["base", "child", "grandchild"])
def relative_path(request):
    """Relative path."""
    return request.param


class TestBaseEndpoint:
    """Class to test base endpoint."""

    def test_default_routes(self, relative_path):
        """Check that rules are applied for all nested routes of the default base endpoint.

        1. Configure application without specifying base endpoint.
        2. Set universal response for all routes.
        3. Make a GET-request to one of the nested endpoints.
        4. Check the response.
        """
        application = configure_application(
            rule_factory=self._rule_factory,
            response_factory=self._response_factory,
            )

        self._set_response(application=application, body=b"body")

        http_response = application.test_client().get(urljoin(DEFAULT_BASE_ENDPOINT, relative_path))
        assert http_response.status_code == 200
        assert http_response.data == b"body", "Wrong response"

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
    def test_routes(self, relative_path, specified_endpoint, expected_endpoint):
        """Check that rules are applied for all nested routes of the specified base endpoint.

        1. Configure application with specifying base endpoint.
        2. Set universal response for all routes.
        3. Make a GET-request to one of the nested endpoints.
        4. Check the response.
        """
        application = configure_application(
            base_endpoint=specified_endpoint,
            rule_factory=self._rule_factory,
            response_factory=self._response_factory,
            )

        self._set_response(application=application, body=b"body")

        http_response = application.test_client().get(urljoin(expected_endpoint, relative_path))
        assert http_response.status_code == 200
        assert http_response.data == b"body", "Wrong response"

    def test_unmanaged_routes(self):
        """Check that only paths nested to the default base endpoint are managed.

        1. Configure application without specifying base endpoint.
        2. Set universal response for all routes.
        3. Make a request to the root.
        4. Check that 404 status is returned.
        """
        application = configure_application(
            rule_factory=self._rule_factory,
            response_factory=self._response_factory,
            )

        self._set_response(application=application, body=b"body")

        assert application.test_client().get("/").status_code == 404, "Wrong status code"

    @pytest.mark.parametrize(
        argnames="method",
        argvalues=["GET", "HEAD", "POST", "PUT", "DELETE", "CONNECT", "OPTIONS", "TRACE", "PATCH"],
        )
    def test_route_methods(self, method):
        """Check that all HTTP methods are allowed for the routes.

        1. Configure application without specifying base endpoint.
        2. Set universal response for all routes.
        3. Make a request of the specified type to the base url.
        4. Check the response.
        """
        application = configure_application(
            rule_factory=self._rule_factory,
            response_factory=self._response_factory,
            )

        self._set_response(application=application, body=b"body")

        http_response = application.test_client().open(DEFAULT_BASE_ENDPOINT, method=method)
        assert http_response.status_code == 200
        # Response for HEAD-request does not contain a body
        assert http_response.data == b"body" or method == "HEAD", "Wrong response"

    @pytest.fixture(autouse=True)
    def _setup_fixtures(
            self,
            rule_factory,
            response_factory,
            server_rule_prototype,
            server_response_prototype,
        ):
        """Setup fixtures."""
        # pylint: disable=attribute-defined-outside-init
        self._rule_factory = rule_factory
        self._response_factory = response_factory
        self._rule_prototype = server_rule_prototype
        self._response_prototype = server_response_prototype

    def _set_response(self, application, body):
        """Set universal response for all dynamic routes."""
        rule = self._rule_prototype.create_new(
            rule_type="Test",
            match_implementation=lambda *args, **kwargs: True,
            )

        self._rule_factory.register_rule(
            rule_type=rule.rule_type,
            parser=lambda *args, **kwargs: rule,
            serializer=lambda *args, **kwargs: {},
            )

        serialized_rule = self._rule_factory.serialize_rule(rule=rule)

        client = application.test_client()
        http_response = client.post(
            urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "rules"),
            json=serialized_rule,
            )

        rule_id = http_response.json["data"]["rule_id"]

        response = self._response_prototype.create_new(
            response_type="Test",
            builder_implementation=lambda *args, **kwargs: body,
            )

        self._response_factory.register_response(
            response_type=response.response_type,
            parser=lambda *args, **kwargs: response,
            serializer=lambda *args, **kwargs: {},
            )

        serialized_response = self._response_factory.serialize_response(response=response)

        client.post(
            urljoin(DEFAULT_CONFIGURATION_ENDPOINT, "response/{0}".format(rule_id)),
            json=serialized_response,
            )
