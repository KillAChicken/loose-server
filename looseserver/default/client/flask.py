"""Module with client to configure server as a flask application."""

from looseserver.client.flask import FlaskClient as BaseFlaskClient
from looseserver.default.client.rule import create_rule_factory
from looseserver.default.client.response import create_response_factory


class FlaskClient(BaseFlaskClient):
    """Class to configure a server via HTTP protocol."""

    def __init__(
            self,
            configuration_url,
            application_client,
            rule_factory=None,
            response_factory=None,
        ):
        if rule_factory is None:
            rule_factory = create_rule_factory()

        if response_factory is None:
            response_factory = create_response_factory()

        super(FlaskClient, self).__init__(
            configuration_url=configuration_url,
            rule_factory=rule_factory,
            response_factory=response_factory,
            application_client=application_client,
            )
