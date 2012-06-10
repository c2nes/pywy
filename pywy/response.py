
import httplib
import StringIO

class Response(object):
    def __init__(self, status=httplib.OK, headers=None, content=""):
        self.status = status
        self.headers = headers if headers else []
        self.content = StringIO.StringIO()

        self.write(content)

    def add_header(self, field_name, field_value):
        self.headers.append((field_name, field_value))

    def write(self, data):
        self.content.write(data)

    def render(self, template, *args, **kwargs):
        rendered = template.render(*args, **kwargs)
        self.write(str(rendered))

    def get_status(self):
        return self.status

    def get_headers(self):
        return self.headers

    def get_content(self):
        return self.content.getvalue()

class HtmlResponse(Response):
    def __init__(self, *args, **kwargs):
        super(HtmlResponse, self).__init__(*args, **kwargs)
        self.add_header("Content-Type", "text/html")

class JsonResponse(Response):
    def __init__(self, *args, **kwargs):
        super(JsonResponse, self).__init__(*args, **kwargs)
        self.add_header("Content-Type", "application/json")

class Redirect(Response):
    def __init__(self, location, redirect_type=httplib.MOVED_PERMANENTLY):
        super(Redirect, self).__init__(status=redirect_type)
        self.add_header("Location", location)
