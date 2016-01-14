import os

VERSION = '0.1'

# Keep a setting for the path to the templates in case a project subclasses the
# models and still needs to use the templates
TEMPLATE_DIR = os.path.join(
    os.path.dirname(__file__),
    'templates')

default_app_config = 'hooks.config.HooksConfig'
