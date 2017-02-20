from django import forms
from .models import Order, Transaction

class OrderCreateForm(forms.Form):
    ISBN = forms.CharField(max_length=20)
    Quantity = forms.IntegerField()

