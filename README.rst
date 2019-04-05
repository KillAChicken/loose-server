loose-server
============
.. image:: https://travis-ci.com/KillAChicken/loose-server.svg?branch=master
    :target: https://travis-ci.com/KillAChicken/loose-server

Loose server is a simple configurable server. It can be used to create temporary servers, dynamically add or remove endpoints and set responses for them from an application.

Usage
=====
Loose server has 2 variations:

- Standalone server with API to manage rules via HTTP.
- Flask application that can be used as a configurable mock in unit-tests.

Standalone server
-----------------
A server can be started by the command::

  $ python -m looseserver.server.run
   * Serving Flask app "run" (lazy loading)
   * Environment: production
     WARNING: Do not use the development server in a production environment.
     Use a production WSGI server instead.
   * Debug mode: off
   * Running on http://127.0.0.1:50000/ (Press CTRL+C to quit)

All configurable endpoint have a common prefix. By default it is ``/routes/``::

  >>> from looseserver.client.http import HTTPClient
  >>> from looseserver.default.client.rule import PathRule
  >>> from looseserver.default.client.response import FixedResponse
  >>> client = HTTPClient(base_url="http://127.0.0.1:50000/_configuration/")
  >>> path_rule_spec = PathRule(path="example")
  >>> path_rule = client.create_rule(rule=path_rule_spec)
  >>> json_response = FixedResponse(status=200, headers={"Content-Type": "application/json"}, body='{"key": "value"}')
  >>> client.set_response(rule_id=path_rule.rule_id, response=json_response)

The response can be obtained by the following response::

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

  >>> from looseserver.server.run import configure_application
  >>> from looseserver.client.flask import FlaskClient
  >>> from looseserver.default.client.rule import PathRule
  >>> from looseserver.default.client.response import FixedResponse
  >>> application = configure_application(base_endpoint="/routes/", configuration_endpoint="/_configuration/")
  >>> client = FlaskClient(base_url="/_configuration/", application_client=application.test_client())
  >>> path_rule_spec = PathRule(path="example")
  >>> path_rule = client.create_rule(rule=path_rule_spec)
  >>> json_response = FixedResponse(status=200, headers={"Content-Type": "application/json"}, body='{"key": "value"}')
  >>> client.set_response(rule_id=path_rule.rule_id, response=json_response)
  >>> response = application.test_client().get("/routes/example")
  >>> response.headers
  Headers([('Content-Type', 'application/json'), ('Content-Length', '16')])
  >>> response.json
  {'key': 'value'}
