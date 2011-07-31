# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag('livedocs/_toc.html', takes_context=True)
def toc(context):
    if 'document_items' in context:
        toc = context['document_items']
    else:
        toc = ''

    return {'toc': toc,
            'item': context.get('item', None),
            'query': context.get('query', None),}