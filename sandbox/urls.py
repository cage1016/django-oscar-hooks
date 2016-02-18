from django.conf.urls import patterns, include, url
from django.conf import settings
from django.contrib import admin
from django.conf.urls.static import static

from hooks.dashboard.app import application as hooks_dashboard
from oscar.app import application

admin.autodiscover()

urlpatterns = [
    url(r'^i18n/', include('django.conf.urls.i18n')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^dashboard/hooks/', include(hooks_dashboard.urls)),
    url(r'', include(application.urls)),
]

if settings.DEBUG:
    import debug_toolbar

    # Server statics and uploaded media
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += patterns('',
                            url(r'^__debug__/', include(debug_toolbar.urls)),
                            )
