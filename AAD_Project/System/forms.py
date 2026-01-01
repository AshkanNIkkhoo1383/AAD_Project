# System/forms.py
from django import forms
from django.forms import formset_factory

class PurchaseItemForm(forms.Form):
    product_id = forms.UUIDField(label="آیدی کالا")
    quantity = forms.IntegerField(min_value=1, label="تعداد")

# Initial visible rows; client-side JS can add more dynamically
PurchaseItemFormSet = formset_factory(PurchaseItemForm, extra=1)
