import sys
import logging
import json
from flask import Flask
import os

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

try:  # werkzeug <= 2.0.3
    from werkzeug.wrappers import BaseRequest
except:  # werkzeug > 2.1
    from werkzeug.wrappers import Request as BaseRequest


logger = logging.getLogger("airview.aws.wrapper")
logger.setLevel(logging.getLevelName(os.getenv("LOG_LEVEL", "INFO")))


def make_environ(event) -> dict:
    """
    Map Lambda Event to WSGI Request
    :param event: Lambda Event
    :return: Mapped Environment Dict
    """
    environ = {}

    for hdr_name, hdr_value in event["headers"].items():
        hdr_name = hdr_name.replace("-", "_").upper()
        if hdr_name in ["CONTENT_TYPE", "CONTENT_LENGTH"]:
            environ[hdr_name] = hdr_value
            continue

        http_hdr_name = "HTTP_%s" % hdr_name
        environ[http_hdr_name] = hdr_value

    query_string = event.get("queryStringParameters", "")

    environ["REQUEST_METHOD"] = event["requestContext"]["httpMethod"]
    environ["PATH_INFO"] = event["path"]
    environ["QUERY_STRING"] = urlencode(query_string) if query_string else ""
    environ["REMOTE_ADDR"] = event["requestContext"]["identity"]["sourceIp"]
    environ["HOST"] = "%(HTTP_HOST)s:%(HTTP_X_FORWARDED_PORT)s" % environ
    environ["SCRIPT_NAME"] = ""
    environ["SERVER_NAME"] = "%(HTTP_HOST)s:%(HTTP_X_FORWARDED_PORT)s" % environ
    environ["SERVER_PORT"] = environ["HTTP_X_FORWARDED_PORT"]
    environ["SERVER_PROTOCOL"] = event["requestContext"]["protocol"]
    environ["CONTENT_LENGTH"] = str(len(event["body"]) if event["body"] else "")
    environ["wsgi.url_scheme"] = environ["HTTP_X_FORWARDED_PROTO"]
    environ["wsgi.input"] = StringIO(event["body"] or "")
    environ["wsgi.version"] = (1, 0)
    environ["wsgi.errors"] = sys.stderr
    environ["wsgi.multithread"] = False
    environ["wsgi.run_once"] = True
    environ["wsgi.multiprocess"] = False

    BaseRequest(environ)
    logger.debug("WSGI Environment: %s", json.dumps(environ, default=str))

    return environ


class LambdaResponse(object):
    def __init__(self):
        self.status = None
        self.response_headers = None

    def start_response(self, status, response_headers, exc_info=None):
        """
        Handle WSGI Response
        :param status: HTTP Status Code
        :param response_headers: Response Headers
        :param exc_info: Exception Info
        """
        logger.debug(
            "Response Started: Status: '%s', Headers: '%s', Exception: '%s'",
            status,
            response_headers,
            exc_info,
        )
        self.status = int(status[:3])
        self.response_headers = dict(response_headers)


class FlaskLambdaHttp(Flask):
    def __call__(self, event: dict, context: dict) -> dict:
        """
        Handle Lambda Event
        :param event: Lambda Event
        :param context: Lambda Context
        :return: Lambda Response JSON Blob
        """
        logger.debug("Lambda Event: %s", json.dumps(event))

        if not event.get("requestContext", {}).get("apiId", None):
            logger.info("Not an API request: Passing request to Flask Superclass")
            return super(FlaskLambdaHttp, self).__call__(event, context)

        response = LambdaResponse()

        body = None
        try:
            body = next(self.wsgi_app(make_environ(event), response.start_response))
        except StopIteration as e:
            ## werkzeug throws a StopIteration error when the response body is empty, which is what we are doing in the
            ## PUT methods on some api services! Need to catch and ignore it here...
            if e.value is None and response.status == 204:
                logger.warning("Request StopIteration Exception on empty response body")
            else:
                raise

        return {
            "statusCode": response.status,
            "headers": response.response_headers,
            "body": body,
        }
