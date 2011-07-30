# -*- coding: utf-8 -*-
from django.contrib import admin
from mptt.admin import MPTTModelAdmin
from models import Item, Version

class ItemAdmin(MPTTModelAdmin):
    list_display = ['slug', 'content']
    pass

admin.site.register(Item, ItemAdmin)
admin.site.register(Version)