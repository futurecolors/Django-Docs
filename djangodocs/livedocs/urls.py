from django.conf.urls.defaults import patterns, url
from django.views.generic.base import TemplateView


urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='livedocs/index.html')),
    url(r'^search/$', 'livedocs.views.search', name='search'),
)
