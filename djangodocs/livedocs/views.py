from annoying.decorators import render_to
from django.db.models.query_utils import Q
from forms import SearchForm
from models import Item

@render_to('livedocs/search.html')
def search(request):
    """ Backend url for searching items"""
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data['query']

    items = Item.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))

    return {'search_form': search_form,
            'query': query,
            'items': items,
            'found_count': len(items)}
