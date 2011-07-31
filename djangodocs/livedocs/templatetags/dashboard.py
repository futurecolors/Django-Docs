# -*- coding: utf-8 -*
from django import template
from livedocs.models import Item


register = template.Library()


@register.inclusion_tag('livedocs/_dashboard.html', takes_context=True)
def dashboard(context):
    panels_data = [
        ['index/s-the-model-layer', 'index/s-the-template-layer', 'index/s-the-view-layer', 'index/forms', ],
        ['index/s-other-batteries-included'],
    ]

    panels = []
    for panel in panels_data:
        items = []
        for path in panel:
            try:
                item = Item.objects.get(path=path,
                                        version__name=context['current_version'],
                                        level=3)
                items.append(item)
            except Item.DoesNotExist, Item.MultipleObjectsReturned:
                pass

        panels.append(items)

    return {'panels': panels}
