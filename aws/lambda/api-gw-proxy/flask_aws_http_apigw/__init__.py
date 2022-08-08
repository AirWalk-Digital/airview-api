import sys

try:
    from urllib import urlencode
except ImportError:
    from urllib.parse import urlencode

from flask import Flask

try:
    from cStringIO import StringIO
except ImportError:
    try:
        from StringIO import StringIO
    except ImportError:
        from io import StringIO

try: # werkzeug <= 2.0.3
    from werkzeug.wrappers import BaseRequest
except: # werkzeug > 2.1
    from werkzeug.wrappers import Request as BaseRequest  # issue fixed by joranbeasley


__version__ = '0.0.4'


def make_environ(event):
    environ = {}

    for hdr_name, hdr_value in event['headers'].items():
        hdr_name = hdr_name.replace('-', '_').upper()
        if hdr_name in ['CONTENT_TYPE', 'CONTENT_LENGTH']:
            environ[hdr_name] = hdr_value
            continue

        http_hdr_name = 'HTTP_%s' % hdr_name
        environ[http_hdr_name] = hdr_value

    qs = event.get('queryStringParameters', "")

    environ['REQUEST_METHOD'] = event['requestContext']['http']['method']
    environ['PATH_INFO'] = event['rawPath']
    environ['QUERY_STRING'] = urlencode(qs) if qs else ''
    environ['REMOTE_ADDR'] = event['requestContext']['http']['sourceIp']
    environ['HOST'] = '%(HTTP_HOST)s:%(HTTP_X_FORWARDED_PORT)s' % environ
    environ['SCRIPT_NAME'] = ''
    environ['SERVER_NAME'] = 'localhost:5000'

    environ['SERVER_PORT'] = environ['HTTP_X_FORWARDED_PORT']
    environ['SERVER_PROTOCOL'] = 'HTTP/1.1'

    environ['CONTENT_LENGTH'] = str(
        len(event['body']) if event['body'] else ''
    )

    environ['wsgi.url_scheme'] = environ['HTTP_X_FORWARDED_PROTO']
    environ['wsgi.input'] = StringIO(event['body'] or '')
    environ['wsgi.version'] = (1, 0)
    environ['wsgi.errors'] = sys.stderr
    environ['wsgi.multithread'] = False
    environ['wsgi.run_once'] = True
    environ['wsgi.multiprocess'] = False

    BaseRequest(environ)

    return environ


class LambdaResponse(object):
    def __init__(self):
        self.status = None
        self.response_headers = None

    def start_response(self, status, response_headers, exc_info=None):
        self.status = int(status[:3])
        self.response_headers = dict(response_headers)


class FlaskLambdaHttp(Flask):
    def __call__(self, event, context):
        if not event.get('requestContext', {}).get('http', None):
            return super(FlaskLambdaHttp, self).__call__(event, context)

        response = LambdaResponse()

        body = next(self.wsgi_app(
            make_environ(event),
            response.start_response
        ))

        return {
            'statusCode': response.status,
            'headers': response.response_headers,
            'body': body
        }
