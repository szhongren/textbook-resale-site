from django import forms
from .models import Book

class SearchForm(forms.Form):
    ISBN = forms.CharField(max_length=20)
