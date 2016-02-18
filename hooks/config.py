from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class HooksConfig(AppConfig):
    label = 'hooks'
    name = 'hooks'
    verbose_name = _('Hooks')

    def ready(self):
        from . import receivers  # noqa
