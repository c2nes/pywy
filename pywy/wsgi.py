
import httplib
import wsgiref

import beaker.session

import pywy.core
import pywy.util

def build_request_object(environ):
    """ Build a PyWy Request object from a WSGI environ object """

    request = pywy.core.Request()

    request.method = environ["REQUEST_METHOD"]
    request.request_uri = wsgiref.util.request_uri(environ)
    request.path = environ["PATH_INFO"]
    request.path_tail = request.path

    session_options = pywy.core.beaker_session_options()
    request.session = beaker.session.SessionObject(environ, **session_options)

    request.base_uri = wsgiref.util.application_uri(environ)
    if request.base_uri[-1] != "/":
        request.base_uri += "/"

    request.get = pywy.util.FieldSet(environ["QUERY_STRING"])

    if request.method == "POST":
        content_length = int(environ["CONTENT_LENGTH"])
        request.post = pywy.util.FieldSet(environ["wsgi.input"].read(content_length))

    return request

def application(pywy):
    def _app(environ, start_response):
        request = build_request_object(environ)
        response = pywy.handle_request(request)

        status = response.get_status()
        status = "%d %s" % (status, httplib.responses[status])
        headers = response.get_headers()
        content = response.get_content()

        start_response(status, headers)

        return [content.encode('utf8')]

    return _app
