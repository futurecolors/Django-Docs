# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from models import Item, Version


class ItemAdmin(MPTTModelAdmin):
    list_display = ['title', 'content', 'slug']
    search_fields = ['title', 'content', 'slug']
    pass

admin.site.register(Item, ItemAdmin)
admin.site.register(Version)
