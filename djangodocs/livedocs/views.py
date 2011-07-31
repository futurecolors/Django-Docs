from annoying.decorators import render_to
from django.core.urlresolvers import resolve, reverse
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views.generic.base import View, RedirectView
from forms import SearchForm
from models import Item, Version

LIMIT_RESULTS = 10

class RedirectToDefaultVersionView(RedirectView):
    def get_redirect_url(self, **kwargs):
        version = Version.objects.get(is_default=True)
        return reverse('search', kwargs={'current_version': version.name})


class BaseLiveView(View):
    def _get_available_docs_versions(self, request, *args, **kwargs):
        """ All available versions of this page (1.3 1.2 dev etc)"""
        match = resolve(request.path)
        avaliable_versions = Version.objects.all().order_by('name')

        for version in avaliable_versions:
            params = kwargs.copy()
            params['current_version'] = version.name
            version.url = reverse(match.url_name, kwargs=params)
            if version.name == kwargs['current_version']:
                version.active = True

        return avaliable_versions

    def get_context(self, request, *args, **kwargs):
        search_form = SearchForm(request.GET)
        if search_form.is_valid():
            query = search_form.cleaned_data['query']
        else:
            query = None

        avaliable_versions = self._get_available_docs_versions(request, *args, **kwargs)

        return {'search_form': search_form,
                'query': query,
                'current_version': kwargs['current_version'],
                'avaliable_versions': avaliable_versions}

    def get_results(self, query, current_version, selected_item=None):
        if not query:
            return {}
            
        items = Item.objects.filter(Q(version__name=current_version),
                            Q(title__icontains=query) | Q(content__icontains=query))[:LIMIT_RESULTS]

        for item in items:
            if item == selected_item or not selected_item:
                item.active = True
                break

        return {'items': items,
                'found_count': items.count()}
    
class SearchView(BaseLiveView):
    @method_decorator(render_to('livedocs/search.html'))
    def get(self, request, *args, **kwargs):
        """ Backend url for searching items"""

        context = self.get_context(request, *args, **kwargs)
        context.update(self.get_results(context['query'], context['current_version']))
        
        if 'found_count' in context:
            context['item'] = context['items'][0]
            context['item_descndants'] = context['item'].get_descendants(include_self=True)

        return context


class ItemView(BaseLiveView):
    @method_decorator(render_to('livedocs/search.html'))
    def get(self, request, *args, **kwargs):
        """ Documentation page"""

        context = self.get_context(request, *args, **kwargs)
        context['item'] = get_object_or_404(Item, path=kwargs['item_path'])
        context['item_descndants'] = context['item'].get_descendants(include_self=True)
        context.update(self.get_results(context['query'], context['current_version'], context['item']))

        return context