
import os
import re

import pywy.config
import pywy.response
import pywy.util

from mako.lookup import TemplateLookup

class Request(object):
    def __init__(self):
        self.method = None
        self.request_uri = None

        self.base_uri = None

        # Portion of the path not consumed by the url matching
        self.path_tail = None
        self.path = None

        self.get = pywy.util.FieldSet()
        self.post = pywy.util.FieldSet()

class PyWyException(Exception):
    pass

class PatternRouter(object):
    """ Regular expession router. Matches expression to beginning of path """

    def __init__(self):
        self.routes = []

    def compile_expression(self, path):
        return re.compile(path)

    def add_route(self, expression, view):
        self.routes.append((re.compile(expression), view))

    def add_routes(self, *args):
        for route in args:
            self.add_route(*route)

    def route(self, app, request):
        path = request.path

        for expression, view in self.routes:
            match = expression.match(path)

            if match:
                parameters = match.groupdict()
                return view(app, request, **parameters)

        return pywy.response.Response(httplib.NOT_FOUND, content="Not found")

class Application(object):
    def __init__(self, app):
        template_dir = os.path.join(pywy.config.APP_DIR, pywy.config.TEMPLATE_DIR)
        self.template_lookup = TemplateLookup(directories=[template_dir])

        self.router = PatternRouter()
        self.router.add_routes(*app.routes)

    def handle_request(self, request):
        # Determine the base uri from the initial request
        if pywy.config.BASE_URI == None:
            pywy.config.BASE_URI = request.base_uri

        # Execute request
        response = self.router.route(self, request)

        # Save session and add cookie header to the response if necesary
        if request.session.accessed():
            request.session.persist()

            session_req = request.session.__dict__['_headers']
            if session_req['set_cookie']:
                cookie = session_req['cookie_out']
                if cookie:
                    response.add_header("Set-cookie", cookie)

        return response

    def render_template(self, template_uri, *args, **data):
        template = self.get_template(template_uri)
        data["config"] = pywy.config
        return template.render(*args, **data)

    def get_template(self, uri):
        return self.template_lookup.get_template(uri)

def beaker_session_options():
    """ Return options dictionary for beaker sessions """

    session_data_dir = os.path.join(pywy.config.APP_DIR, pywy.config.SESSION_DIR)
    options = dict(invalidate_corrupt=True, type='file',
                   data_dir=session_data_dir, timeout=None,
                   secret=None, log_file=None, auto=True)

    return options
