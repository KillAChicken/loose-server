loose-server
============
.. image:: https://travis-ci.com/KillAChicken/loose-server.svg?branch=master
    :target: https://travis-ci.com/KillAChicken/loose-server

Loose server is a simple configurable server. It can be used to create temporary servers, dynamically add or remove endpoints and set responses for them from an application.

Installation
============

.. code-block:: text

    $ python -m pip install loose-server

Additional packages will be installed: ``Flask``, ``flask-restful`` (required for the server) and ``requests`` (required for the http clients).

Documentation
=============
Documentation for the package can be found on the `Wiki <https://github.com/KillAChicken/loose-server/wiki>`_.

Quickstart
==========
Loose server has 2 variations:

- Standalone server with API to manage rules via HTTP.
- Flask application that can be used as a configurable mock in unit-tests.

Standalone server
-----------------
A server can be started by the command

.. code-block:: text

    $ python -m looseserver.default.server.run
     * Serving Flask app "looseserver" (lazy loading)
     * Environment: production
       WARNING: Do not use the development server in a production environment.
       Use a production WSGI server instead.
     * Debug mode: off
     * Running on http://127.0.0.1:50000/ (Press CTRL+C to quit)

API endpoints are nested to the base configuration url. By default it is ``/_configuration/``.

.. code-block:: python

    from looseserver.default.client.rule import PathRule
    from looseserver.default.client.response import FixedResponse
    from looseserver.default.client.http import HTTPClient

    client = HTTPClient(configuration_url="http://127.0.0.1:50000/_configuration/")

    path_rule = client.create_rule(rule=PathRule(path="example"))

    json_response = FixedResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body='{"key": "value"}',
        )
    client.set_response(rule_id=path_rule.rule_id, response=json_response)

All configured endpoints have a common prefix. By default it is ``/routes/``.
The response can be obtained by the following request

.. code-block:: text

  $ curl http://127.0.0.1:50000/routes/example -i
  HTTP/1.0 200 OK
  Content-Type: application/json
  Content-Length: 16
  Server: Werkzeug/0.15.2 Python/3.5.2
  Date: Fri, 05 Apr 2019 14:08:50 GMT

  {"key": "value"}

Configurable mock
-----------------
Loose server can be used as a mock server in the following way

.. code-block:: python

    from looseserver.default.server.application import configure_application
    from looseserver.default.client.flask import FlaskClient
    from looseserver.default.client.rule import PathRule
    from looseserver.default.client.response import FixedResponse

    application = configure_application(base_endpoint="/base/", configuration_endpoint="/config/")
    app_client=application.test_client()

    client = FlaskClient(configuration_url="/config/", application_client=app_client)

    path_rule = client.create_rule(rule=PathRule(path="example"))

    json_response = FixedResponse(
        status=200,
        headers={"Content-Type": "application/json"},
        body='{"key": "value"}',
        )
    client.set_response(rule_id=path_rule.rule_id, response=json_response)

    response = app_client.get("/base/example")
    assert response.headers["Content-Type"] == "application/json"
    assert response.json == {'key': 'value'}
