# -*- coding: utf-8 -*-
from django import template

register = template.Library()

@register.filter()
def get_header(value, arg):
    return value.level - arg.level + 1
