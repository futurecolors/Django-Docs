from annoying.decorators import render_to
from django.db.models.query_utils import Q
from livedocs.models import Item

@render_to('livedocs/search.html')
def search(request):
    """ Backend url for searching items"""

    query = request.GET.get('query', '')
    items = Item.objects.filter(Q(title__icontains=query) | Q(content__icontains=query))

    return {'query': query,
            'items': items,
            'found_count': len(items)}
