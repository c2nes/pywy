
import os

from mako.lookup import TemplateLookup

class TemplateContext(object):
    def __init__(self, application):
        template_dir = os.path.join(application.config.APP_DIR,
                                    application.config.TEMPLATE_DIR)

        self.application = application
        self.lookup = TemplateLookup(directories=[template_dir])

    def render(self, template_uri, *args, **data):
        template = self.get(template_uri)

        # Add config to variables
        data["config"] = self.application.config

        return template.render(*args, **data)

    def get(self, uri):
        return self.lookup.get_template(uri)
