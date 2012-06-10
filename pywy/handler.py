
import mimetypes
import os

import pywy.response
import pywy.config

class ApplicationRedirectHandler(object):
    def __init__(self, location):
        self.location = location

        # Remove leading /
        if self.location[0] == "/":
            self.location = self.location[1:]

    def __call__(self, app, request):
        return pywy.response.Redirect(pywy.config.BASE_URI + self.location)

class AbsoluteRedirectHandler(object):
    def __init__(self, location):
        self.location = location

    def __call__(self, app, request):
        return pywy.response.Redirect(self.location)

class TemplateHandler(object):
    def __init__(self, template_uri, *args, **kwargs):
        self.uri = template_uri
        self.args = args
        self.kwargs = kwargs

    def __call__(self, app, request):
        response = pywy.response.HtmlResponse()
        response.write(app.render_template("index.html", *self.args, **self.kwargs))

        return response

class StaticContentHandler(object):
    def __init__(self, uri_prefix, base_path):
        self.uri_prefix = uri_prefix
        self.base_path = base_path
        self.mimedb = mimetypes.MimeTypes()

    def __get_filesystem_path(self, request):
        path = request.path

        # Remove prefix
        path = path[len(self.uri_prefix):]

        # Join with base filesystem path
        path = os.path.join(self.base_path, path)

        # Normalize path
        path = os.path.abspath(path)

        # Check that path is still under the base path
        prefix = os.path.commonprefix([self.base_path, path])

        if prefix != self.base_path:
            return None

        return path

    def __call__(self, app, request):
        path = self.__get_filesystem_path(request)

        if path == None or not os.path.isfile(path):
            return pywy.response.Response(httplib.NOT_FOUND)

        mimetype, encoding = self.mimedb.guess_type(path)

        if not mimetype:
            mimetype = "application/octet-stream"

        response = pywy.response.Response()
        response.add_header("Content-Type", mimetype)

        with open(path) as f:
            response.write(f.read())

        return response
