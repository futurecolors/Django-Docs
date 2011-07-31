from django.views.generic import RedirectView, TemplateView
import os
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from livedocs.views import IndexView
from settings import STATIC_ROOT, ROOT_PATH


admin.autodiscover()

urlpatterns = staticfiles_urlpatterns()

urlpatterns += patterns('',
    # Static
    (r'^(favicon.ico)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
    (r'^(robots.txt)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),
    (r'^(humans.txt)$', 'django.views.static.serve', {'document_root': STATIC_ROOT}),

    url(r'^$', IndexView.as_view()),
    url(r'^admin/', include(admin.site.urls)),
    url(r'(?P<current_version>[^/]+?)/', include('livedocs.urls')),
    (r'^data/(?P<path>.*)', 'django.views.static.serve', {'document_root': os.path.join(ROOT_PATH, 'livedocs/data'),
                                                          'show_indexes': True}),

)


