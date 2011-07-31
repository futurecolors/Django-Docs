from annoying.decorators import render_to
from django.core.urlresolvers import resolve, reverse
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View, RedirectView
from forms import SearchForm
from models import Item, Version


class RedirectToDefaultVersionView(RedirectView):
    def get_redirect_url(self, **kwargs):
        version = Version.objects.get(is_default=True)
        return reverse('search', kwargs={'current_version': version.name})


class BaseLiveView(View):
    def get_context(self, request, *args, **kwargs):
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
        else:
            query = None

        match = resolve(request.path)
        avaliable_versions = Version.objects.all().order_by('name')
        for version in avaliable_versions:
            params = kwargs.copy()
            params['current_version'] = version.name
            version.url = reverse(match.url_name, kwargs=params)
            if version.name == kwargs['current_version']:
                version.selected = True

        return {'search_form': search_form,
                'query': query,
                'current_version': kwargs['current_version'],
                'avaliable_versions': avaliable_versions}

    
class SearchView(BaseLiveView):
    @method_decorator(render_to('livedocs/search.html'))
    def get(self, request, *args, **kwargs):
        """ Backend url for searching items"""

        context = self.get_context(request, *args, **kwargs)

        if context['query']:
            context['items'] = Item.objects.filter(Q(version__name=context['current_version']),
                                Q(title__icontains=context['query']) | Q(content__icontains=context['query']))[:10]
            context['found_count'] = context['items'].count()
            if context['found_count']:
                context['item'] = context['items'][0]

        return context


class ItemView(BaseLiveView):
    @method_decorator(render_to('livedocs/item.html'))
    def get(self, request, *args, **kwargs):
        """ Documentation page"""

        context = self.get_context(request, *args, **kwargs)
        context['item'] = get_object_or_404(Item, path=kwargs['item_path'])

        return context