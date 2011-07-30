from django.conf.urls.defaults import patterns, url
from django.views.generic.base import TemplateView
from views import SearchView, ItemView


urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='livedocs/index.html')),
    #url(r'^search/$', 'livedocs.views.search', name='search'),
    url(r'^search/$', SearchView.as_view(), name='search'),
    url(r'^(?P<item_path>.*)/$', ItemView.as_view(), name='item'),
)
