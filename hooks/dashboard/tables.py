from django.utils.translation import ugettext_lazy as _
from django_tables2 import A, TemplateColumn

from oscar.core.loading import get_class, get_model
import django_tables2 as tables

DashboardTable = get_class('dashboard.tables', 'DashboardTable')

Hook = get_model('hooks', 'Hook')
HookLog = get_model('hooks', 'HookLog')


class HookTable(DashboardTable):
  name = TemplateColumn(
      verbose_name=_("Name"),
      template_name='hooks/dashboard/hook_row_name.html',
      order_by='name', accessor=A('name'),
  )
  actions = TemplateColumn(
      verbose_name=_('Actions'),
      template_name='hooks/dashboard/hook_row_actions.html',
      orderable=False)

  icon = 'sitemap'

  class Meta(DashboardTable.Meta):
    model = Hook
    fields = ('name', 'product', 'hook_class', 'hookevent__count', 'date_updated',)
    order_by = '-date_updated'


class HookLogTable(DashboardTable):
  signal_type_name = tables.Column()

  class Meta(DashboardTable.Meta):
    model = HookLog
    fields = (
      'signal_type_name',
      'request_url',
      'data', 'headers', 'response', 'status', 'retry', 'error_message', 'date_created',)
