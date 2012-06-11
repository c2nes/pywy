
import imp
import os
import sys
import ConfigParser

import pywy.core

__all__ = ["open_application", "config", "application", "template"]

# Global config object
config = None

# Global application object
application = None

# Global template context object
template = None

def load_module(name):
    if name in sys.modules:
        return sys.modules[name]
    return __import__(name)

def open_application(app_dir, register_globally=True):
    """ Open the application located at the application directory given by
    `app_dir`.

    The application directory should contain a config.ini file. This file must
    specify an app_name option. This name refers to a module by the same name
    located in the application directory.

    If register_globally is true than the application registers global
    psuedo-modules pywy.config, pywy.application, and pywy.template.
    """

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
    local_config = pywy.core.Config()
    local_config.update(options)

    # Register config globally before loading application modules since module
    # level code in applications may well need access to this to establish
    # routes
    if register_globally:
        global config
        config = local_config

    try:
        application_module = load_module(config.APP_NAME)
    except ImportError:
        raise pywy.core.PyWyException("Could not load application module")

    new_application = pywy.core.Application(application_module, local_config)

    if register_globally:
        # Create module level application objects representing the currently
        # running application
        global application, template

        application = new_application
        template = new_application.template

    return new_application
