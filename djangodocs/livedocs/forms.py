# -*- coding: utf-8 -*-
from django import forms

class SearchForm(forms.Form):
    query = forms.CharField(label='', widget=forms.TextInput(attrs={'class':'b-search__keyword'}))