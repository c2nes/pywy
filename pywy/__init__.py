
import imp
import os
import sys
import ConfigParser

import pywy.core

def load_module(name):
    if name in sys.modules:
        return sys.modules[name]
    return __import__(name)

def open_application(app_dir):
    if app_dir not in sys.path:
        sys.path.append(base_path)

    config_file = os.path.join(app_dir, "config.ini")

    parser = ConfigParser.SafeConfigParser()
    if not parser.read(config_file):
        raise PyWyException("Configuration file could not be opened")

    # Get all options in the pywy section
    try:
        options = parser.items("pywy")
    except ConfigParser.NoSectionError:
        raise pywy.core.PyWyException("No pywy section found in configuration file")

    options = dict([(key.lower(), value) for key, value in options])

    # Load application configuration
    pywy.config.set_application_config(options)

    try:
        application_module = load_module(config.APP_NAME)
    except ImportError:
        raise pywy.core.PyWyException("Could not load application module")

    return pywy.core.Application(application_module)

class Config(object):
    def __init__(self):
        self.app_config = None
        self.defaults = dict()

    def set_application_config(self, app_config):
        self.app_config = app_config

    def set(self, option, value):
        self.defaults[option.lower()] = value

    def __getattr__(self, attr):
        attr = attr.lower()

        if attr in self.app_config:
            return self.app_config[attr]
        elif attr in self.defaults:
            return self.defaults[attr]
        else:
            return None

config = Config()
