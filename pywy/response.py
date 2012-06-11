
import pywy.core

class HtmlResponse(pywy.core.Response):
    def __init__(self, *args, **kwargs):
        super(HtmlResponse, self).__init__(*args, **kwargs)
        self.add_header("Content-Type", "text/html")

class JsonResponse(pywy.core.Response):
    def __init__(self, *args, **kwargs):
        super(JsonResponse, self).__init__(*args, **kwargs)
        self.add_header("Content-Type", "application/json")

class Redirect(pywy.core.Response):
    def __init__(self, location, redirect_type=pywy.codes.MOVED_PERMANENTLY):
        super(Redirect, self).__init__(status=redirect_type)
        self.add_header("Location", location)
