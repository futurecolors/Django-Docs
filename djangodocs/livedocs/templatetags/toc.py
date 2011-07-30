# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.inclusion_tag('livedocs/_toc.html', takes_context=True)
def toc(context):
    if 'item' in context:
        toc = context['item'].get_ancestors()
    else:
        toc = ''

    return {'toc': toc}