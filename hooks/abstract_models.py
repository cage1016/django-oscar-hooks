from django.conf import settings
from django.db import models
from jsonfield import JSONField
from django.utils.encoding import python_2_unicode_compatible
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from oscar.models.fields import AutoSlugField, NullCharField
from oscar.core.compat import AUTH_USER_MODEL

from datetime import datetime

try:
  from oscar.apps.catalogue.models import Product

except ImportError:
  Product = getattr(settings, 'Product', 'oscar.apps.catalogue.models')


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
class AbstractHookClass(models.Model):
  """
  // TDOD
  """

  name = models.CharField(_('Name'), max_length=128)

  slug = AutoSlugField(_('Slug'), max_length=128, unique=True, populate_from='name')

  email = models.EmailField(_("Hook error report email"), max_length=75, blank=True)

  user = models.ForeignKey(
      AUTH_USER_MODEL, related_name="hookClasses",
      blank=True, verbose_name=_("User"), null=True)

  class Meta:
    abstract = True
    app_label = 'hooks'
    ordering = ['name']
    verbose_name = _("Hook class")
    verbose_name_plural = _("Hook classes")

  def __str__(self):
    return self.name


@python_2_unicode_compatible
class AbstractHook(models.Model):
  name = models.CharField(max_length=128, unique=True, null=True, blank=True)

  slug = AutoSlugField(_('Slug'), max_length=255, unique=False, populate_from='name')

  description = models.TextField(_('Description'), blank=True, null=True)

  hook_class = models.ForeignKey(
      'hooks.HookClass', null=True, blank=True, on_delete=models.PROTECT,
      verbose_name=_('Hook type'), related_name="hooks",
      help_text=_("Choose what hook type of hook this is")
  )

  product = models.ForeignKey(
      Product, null=True, blank=True, on_delete=models.PROTECT,
      verbose_name=_("Product"), help_text=_("What kind of product that hook belong to.")
  )

  date_created = models.DateTimeField(_("Date created"), null=True, default=datetime.now)

  # This field is used by Haystack to reindex search
  date_updated = models.DateTimeField(_("Date updated"), db_index=True, null=True, default=datetime.now)

  class Meta:
    abstract = True
    app_label = 'hooks'
    ordering = ['-date_created']
    verbose_name = _("Hook")
    verbose_name_plural = _("Hook")

  def __str__(self):
    return self.name

  def save(self, *args, **kwargs):
    return super(AbstractHook, self).save(*args, **kwargs)

  def as_dict(self):
    return NotImplementedError

  def get_hook_class(self):
    """
    :return: a hook's item class.
    """
    return self.hook_class


SUPPORT_SINGALS = (
  (u'1', u'product_viewed'),
  # (u'2', u'user_search'),
  # (u'3', u'user_registered'),
  # (u'4', u'basket_addition'),
  # (u'5', u'voucher_addition'),
  # (u'6', u'start_checkout'),
  (u'7', u'pre_payment'),
  (u'8', u'post_payment'),
  (u'9', u'order_placed'),
  (u'10', u'post_checkout'),
  (u'11', u'review_added'),
)


class AbstractHookEvent(models.Model):
  hook = models.ForeignKey(
      'hooks.Hook', null=True, blank=True, on_delete=models.PROTECT,
      verbose_name=_("Hook"), help_text=_("Choose what hook of hook URL")
  )

  signal_type = models.CharField(max_length=2, choices=SUPPORT_SINGALS)

  URL = models.URLField(blank=True)

  extra_headers = JSONField(null=True, blank=True)

  class Meta:
    abstract = True
    app_label = "hooks"
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

  @property
  def signal_type_name(self):
    return dict(SUPPORT_SINGALS).get(self.signal_type)
