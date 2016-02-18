from django.conf.urls import url

from oscar.core.application import Application
from oscar.core.loading import get_class


class HooksDashboardApplication(Application):
    name = None

    default_permissions = ['is_staff', ]
    permissions_map = {
        'hook-list': (['is_staff'], ['partner.dashboard_access']),
        'hook-delete': (['is_staff'], ['partner.dashboard_access']),
        'hook': (['is_staff'], ['partner.dashboard_access']),
        'hook-create': (['is_staff'], ['partner.dashboard_access']),
        'hook-logs': (['is_staff'], ['partner.dashboard_access']),
        'signal-type-lookup': (['is_staff'], ['partner.dashboard_access']),
    }

    hook_list = get_class('hooks.dashboard.views', 'HookListView')
    hook_delete_view = get_class('hooks.dashboard.views', 'HookDeleteView')
    hook_create_redirect_view = get_class('hooks.dashboard.views', 'HookCreateRedirectView')
    hook_createupdate_view = get_class('hooks.dashboard.views', 'HookCreateUpdateView')

    signal_type_lookup_view = get_class('hooks.dashboard.views', 'SingalTypeLookupView')

    hook_logs_view = get_class('hooks.dashboard.views', 'HookLogsView')

    def get_urls(self):
        urlpatterns = [
            url(r'^$', self.hook_list.as_view(), name='hook-list'),

            url(r'^hook/(?P<pk>\d+)/delete/$', self.hook_delete_view.as_view(), name='hook-delete'),
            url(r'^hook/(?P<pk>\d+)/$', self.hook_createupdate_view.as_view(), name='hook'),

            url(r'^hooks/create/$', self.hook_create_redirect_view.as_view(), name='hook-create'),
            url(r'^hooks/create/(?P<hook_class_slug>[\w-]+)/$', self.hook_createupdate_view.as_view(),
                name='hook-create'),

            url(r'^signal-type-lookup/$', self.signal_type_lookup_view.as_view(), name='signal-type-lookup'),

            url(r'^logs/$', self.hook_logs_view.as_view(), name='hook-logs'),
        ]
        return self.post_process_urls(urlpatterns)


application = HooksDashboardApplication()
