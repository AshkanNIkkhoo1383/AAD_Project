# System/forms.py
from django import forms
from django.forms import formset_factory
from .models import Attendance

class PurchaseItemForm(forms.Form):
    product_id = forms.UUIDField(label="آیدی کالا")
    quantity = forms.IntegerField(min_value=1, label="تعداد")
# Initial visible rows; client-side JS can add more dynamically
PurchaseItemFormSet = formset_factory(PurchaseItemForm, extra=1)
class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['check_in', 'check_out', 'status', 'notes']
class DateRangeForm(forms.Form):
    start_date = forms.DateField(label="از تاریخ", widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label="تا تاریخ", widget=forms.DateInput(attrs={'type': 'date'}))

#<!--{{ item.quantity|mul:item.product.price }}تومان-->