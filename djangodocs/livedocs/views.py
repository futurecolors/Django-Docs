from annoying.decorators import render_to
from django.core.urlresolvers import resolve, reverse
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View
from forms import SearchForm
from models import Item, Version


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
            version.url = reverse(match.url_name, kwargs=kwargs)
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
                                        Q(title__icontains=context['query']) | Q(content__icontains=context['query']))
            context['found_count'] = context['items'].count()

        return context


class ItemView(BaseLiveView):
    @method_decorator(render_to('livedocs/item.html'))
    def get(self, request, *args, **kwargs):
        """ Documentation page"""

        context = self.get_context(request, *args, **kwargs)
        context['item'] = get_object_or_404(Item, path=kwargs['item_path'])

        return context