from django.conf.urls.defaults import patterns, url
from django.views.generic.base import TemplateView


urlpatterns = patterns('',
    url(r'^$', TemplateView.as_view(template_name='livedocs/index.html')),

    # Markup
    url(r'^markup/index/', TemplateView.as_view(template_name='livedocs/markup/index.html')),
)
