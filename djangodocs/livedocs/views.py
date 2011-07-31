import urllib
from annoying.decorators import render_to
from django.core.urlresolvers import resolve, reverse
from django.db.models.query_utils import Q
from django.shortcuts import get_object_or_404, redirect
from django.utils.decorators import method_decorator
from django.views.generic.base import View, RedirectView, TemplateView
from djangosphinx.models import SphinxQuerySet, SearchError
from forms import SearchForm
from models import Item, Version

LIMIT_RESULTS = 10


def ajax_headers(view_func):
    '''Pass page title or redirect in X-Ajax-* headers for hash-based urls'''
    def _add_header(response, template_variable, header_name):
        '''Take header value from template and put in reponse header'''
        header_value = response.context_data.get(template_variable, None)
        if header_value:
            response[header_name] = urllib.quote(header_value.encode('utf-8'))
        return response


    def _wrapped_view_func(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        if request.is_ajax():
            response = _add_header(response, 'ajax_redirect', 'X-Ajax-Redirect')
            response = _add_header(response, 'title', 'X-Ajax-PageTitle')
        return response
    return _wrapped_view_func


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
                'avaliable_versions': avaliable_versions,
                'body_template': 'livedocs/layout/ajax.html' if request.is_ajax() else 'livedocs/layout/body.html'}

    def get_results(self, query, current_version, selected_item=None):
        if not query:
            return {}

        version = Version.objects.get(name=current_version)
        try:
            sphinx_result = SphinxQuerySet(index='items').query(query)
            result_items_list = [r for r in sphinx_result if r.version == version]
            items = result_items_list[:LIMIT_RESULTS]
            found_count = len(items)
        except SearchError:
            items = Item.objects.filter(Q(version=version),
                                Q(title__icontains=query) | Q(content__icontains=query))[:LIMIT_RESULTS]
            found_count = items.count()

        for item in items:
            if item == selected_item or not selected_item:
                item.active = True
                break

        return {'items': items,
                'found_count': found_count}

    
class IndexView(TemplateView):
    template_name = 'livedocs/index.html'

    def get_context_data(self, **kwargs):
        version = Version.objects.get(is_default=True)
        return {
            'body_template': 'livedocs/layout/body.html',
            'default_version_url': reverse('index', kwargs={'current_version': version.name}),
            'current_version': version.name
        }


class SearchView(BaseLiveView):
    @method_decorator(render_to('livedocs/search.html'))
    def get(self, request, *args, **kwargs):
        """ Backend url for searching items"""

        context = self.get_context(request, *args, **kwargs)
        context.update(self.get_results(context['query'], context['current_version']))

        if not context['query']:
            context['title'] = 'Search'
        elif context['found_count']:
            context['item'] = context['items'][0]
            context['document_items'] = context['item'].get_document_nodes()
            context['title'] = context['item'].title
        else:
            context['title'] = 'No results'

        return context


class ItemView(BaseLiveView):
    @method_decorator(render_to('livedocs/search.html'))
    def get(self, request, *args, **kwargs):
        """ Documentation page"""

        context = self.get_context(request, *args, **kwargs)
        context['item'] = get_object_or_404(Item, path=kwargs['item_path'], version__name=context['current_version'])
        context['document_items'] = context['item'].get_document_nodes()
        context.update(self.get_results(context['query'], context['current_version'], context['item']))

        return context
