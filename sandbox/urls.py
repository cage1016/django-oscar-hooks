from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf import settings
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

from hooks.dashboard.app import application as hooks_dashboard
from oscar.app import application

admin.autodiscover()

urlpatterns = patterns(
    '',
    (r'^admin/', include(admin.site.urls)),
    url(r'^dashboard/hooks/', include(hooks_dashboard.urls)),
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'', include(application.urls)),
)

if settings.DEBUG:
  urlpatterns += staticfiles_urlpatterns()
  urlpatterns += static(
      settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
