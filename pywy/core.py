
import os
import re
import StringIO

import pywy.codes
import pywy.util
import pywy.templatecontext

__all__ = ["PyWyException", "PyWy404", "Request", "Respones", "Application"]

class PyWyException(Exception):
    pass

class PyWy404(Exception):
    """ Raise a 404 error response """
    pass

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

        # Application associated with this request
        self.application = None

class Response(object):
    def __init__(self, status=pywy.codes.OK, headers=None, content=""):
        self.status = status
        self.headers = headers if headers else []
        self.content = StringIO.StringIO()

        self.write(content)

    def add_header(self, field_name, field_value):
        self.headers.append((field_name, field_value))

    def write(self, data):
        self.content.write(data)

    def get_status(self):
        return self.status

    def get_headers(self):
        return self.headers

    def get_content(self):
        return self.content.getvalue()

class Application(object):
    def __init__(self, app, config):
        self.config = config
        self.template = pywy.templatecontext.TemplateContext(self)

        # The application must provide a list of routes in its top level module
        # or a function returning such a list. Each route is a 2-tuple with a
        # regular expression to match URLs and a callable view function.

        self.router = PatternRouter()

        if hasattr(app, "routes"):
            self.router.add_routes(*app.routes)

        elif hasattr(ap, "get_routes"):
            routes = app.get_routes(self)
            self.router.add_routes(*routes)

        else:
            raise PyWyException("No routes available within application package")

    def handle_request(self, request):
        # Determine the base uri from the initial request if one is not
        # explicitly set
        if self.config.BASE_URI == None:
            self.config.set("BASE_URI", request.base_uri)

        # Get view and execute request
        view, parameters = self.router.route(request)
        response = view(request, **parameters)

        # Save session and add cookie header to the response if necesary
        if request.session.accessed():
            request.session.persist()

            session_req = request.session.__dict__['_headers']
            if session_req['set_cookie']:
                cookie = session_req['cookie_out']
                if cookie:
                    response.add_header("Set-cookie", cookie)

        return response

class Config(object):
    def __init__(self):
        self.options = dict()

    def update(self, config):
        self.options.update(config)

    def set(self, option, value):
        self.options[option.lower()] = value

    def get(self, option, default=None):
        return self.options.get(option.lower(), None)

    def __getattr__(self, attr):
        """ Retrieve options as attributes """
        return self.get(attr)

    @property
    def beaker_session_options(self):
        """ Return options dictionary for beaker sessions """

        session_data_dir = os.path.join(self.APP_DIR, self.SESSION_DIR)

        # TODO: Options which should be made into PyWy application options
        options = dict(type='file',
                       data_dir=session_data_dir,
                       auto=True)

        # Standard options
        options.update(invalidate_corrupt=True, timeout=None,
                       secret=None, log_file=None,)

        return options

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

    def route(self, request):
        path = request.path

        for expression, view in self.routes:
            match = expression.match(path)

            if match:
                parameters = match.groupdict()
                return view, parameters

        raise PyWy404()
