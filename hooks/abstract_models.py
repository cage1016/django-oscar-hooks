from django.conf import settings
from django.db import models
from jsonfield import JSONField
# import jsonfield
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from slugify import slugify

from oscar.models.fields import AutoSlugField
from oscar.core.compat import AUTH_USER_MODEL

from datetime import datetime

try:
    from oscar.apps.catalogue.models import ProductClass

except ImportError:
    ProductClass = getattr(settings, 'ProductClass', 'oscar.apps.catalogue.models')


class ActiveHookManager(models.Manager):
    def get_queryset(self):
        now = timezone.now()
        qs = super(ActiveHookManager, self).get_queryset()
        return qs.filter(
                models.Q(start_date__lte=now) |
                models.Q(start_date=None)).filter(
                models.Q(end_date__gte=now) |
                models.Q(end_date=None))


@python_2_unicode_compatible
class AbstractHook(models.Model):
    name = models.CharField(_('Name'), max_length=128)

    error_report_email = models.EmailField(_('Error Report Email'), blank=False, default='')

    slug = AutoSlugField(_('Slug'), max_length=255, unique=False, populate_from='name')

    description = models.TextField(_('Description'), blank=True, null=True)

    product_class = models.ForeignKey(
            ProductClass, null=True, blank=True, on_delete=models.PROTECT,
            verbose_name=_('Product type'), related_name="Product.product_class+",
            help_text=_("Choose what type of product this is"))

    user = models.ForeignKey(
            AUTH_USER_MODEL, related_name="hookClasses",
            blank=True, verbose_name=_("User"), null=True)

    date_created = models.DateTimeField(_("Date created"), null=True, default=datetime.now)

    # This field is used by Haystack to reindex search
    date_updated = models.DateTimeField(_("Date updated"), db_index=True, null=True, default=datetime.now)

    event_count = models.PositiveSmallIntegerField(_("HookEvent Count"), default=0)

    class Meta:
        abstract = True
        app_label = 'hooks'
        ordering = ['-date_created']
        verbose_name = _("Hook")
        verbose_name_plural = _("Hook")

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        return super(AbstractHook, self).save(*args, **kwargs)

    def as_dict(self):
        return NotImplementedError

    def get_product_class(self):
        """
        :return: a hook's item class.
        """
        return self.product_class


class AbstractSignalType(models.Model):
    name = models.CharField(max_length=30)

    class Meta:
        abstract = True
        app_label = "hooks"
        verbose_name = _("Hook Signal")
        verbose_name_plural = _("Hook Signals")

    def __str__(self):
        return self.name


class AbstractHookEvent(models.Model):
    hook = models.ForeignKey(
            'hooks.Hook', null=True, blank=True, on_delete=models.PROTECT, verbose_name=_("Hook"))

    signal_type = models.ForeignKey(
            'hooks.HookSignalType', verbose_name=_("Signal Type"), null=True, blank=True)

    URL = models.URLField(blank=True)

    extra_headers = JSONField(default={})

    class Meta:
        abstract = True
        app_label = "hooks"
        unique_together = ('hook', 'signal_type')
        verbose_name = _("Hook URL")

    def __str__(self):
        return self.summary()

    def summary(self):
        """
        Gets a string representation of both the attribute and it's value,
        used e.g in product summaries.
        """
        return u"%s: %s" % (self.signal_type, self.URL)


class AbstractHookLog(models.Model):
    hook_event = models.ForeignKey("hooks.HookEvent", null=True, blank=True, verbose_name=_("Hook Event"))

    signal_type = models.CharField(_('Signal Type'), max_length=40, null=False)

    data = models.TextField(_('Data'), null=False)

    headers = JSONField(_('Headers'), null=False)

    request_url = models.URLField(_('Request Url'), null=False, blank=True)

    response = JSONField(_('Response'), null=False)

    status = models.IntegerField(_('Status'), null=True)

    retry = models.IntegerField(_('Retry Count'), default=0)

    error_message = models.TextField(_('Error Message'), null=True, blank=True)

    date_created = models.DateTimeField(_("Date created"), null=True, default=datetime.now)

    class Meta:
        abstract = True
        app_label = 'hooks'
        ordering = ['-date_created']
        verbose_name = _("HookLog")
        verbose_name_plural = _("HookLog")

    def __str__(self):
        return '%s-%s' % (self.product, self.signal_type)

    def as_dict(self):
        return NotImplementedError
