from django.views.generic.base import RedirectView
import os
from django.conf.urls.defaults import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib import admin
from settings import STATIC_ROOT, ROOT_PATH


admin.autodiscover()


urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='1.3/')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'(?P<current_version>[^/]+?)/', include('livedocs.urls')),
    (r'^data/(?P<path>.*)', 'django.views.static.serve', {'document_root': os.path.join(ROOT_PATH, 'livedocs/data'),
                                                          'show_indexes': True}),

)

urlpatterns += staticfiles_urlpatterns()
