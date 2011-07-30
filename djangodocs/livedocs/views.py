from annoying.decorators import render_to
from django.db.models.query_utils import Q
from forms import SearchForm
from models import Item, Version

@render_to('livedocs/search.html')
def search(request, current_version):
    """ Backend url for searching items"""
    search_form = SearchForm(request.GET)
    if search_form.is_valid():
        query = search_form.cleaned_data['query']

    items = Item.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))
    
    avaliable_versions = Version.objects.all().order_by('name')
    for version in avaliable_versions:
        if version.name == current_version:
            version.selected = True

    return {'search_form': search_form,
            'version': version,
            'avaliable_versions': avaliable_versions,
            'query': query,
            'items': items,
            'found_count': len(items)}
