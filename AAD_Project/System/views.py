from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin 
from django.views.generic.detail import DetailView 
from django.urls import reverse_lazy
from .models import CustomUser , Product ,Inventory, CustomerPurchase, PurchaseItem
from .forms import PurchaseItemFormSet 
from django.contrib import messages
from django.db import transaction 
from django.views import View 

class CustomLoginView(LoginView):
    template_name = "login.html"   # قالب صفحه ورود
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        # بررسی نقش کاربر
        if user.position == "storemanager":
            return reverse_lazy("storemanager_dashboard")  # صفحه مدیر فروشگاه
        else:
            return reverse_lazy("employee_dashboard")      # صفحه کارمند

class ProductDetailView(LoginRequiredMixin, DetailView):
    model = Product
    template_name = "product_detail.html"
    context_object_name = "product"
    login_url = reverse_lazy("login") # مسیر صفحه لاگین در صورت عدم ورود
class MultiPurchaseCreateView(LoginRequiredMixin, View):
    template_name = "multi_purchase_create.html"
    login_url = reverse_lazy("login")

    def get(self, request):
        formset = PurchaseItemFormSet()
        return render(request, self.template_name, {"formset": formset})

    def post(self, request):
        formset = PurchaseItemFormSet(request.POST)

        if not formset.is_valid():
            messages.error(request, "ورودی‌ها معتبر نیستند.")
            return render(request, self.template_name, {"formset": formset})

        # Filter out entirely empty forms (when user added extra rows but left them blank)
        cleaned_forms = [
            f for f in formset
            if f.cleaned_data.get("product_id") and f.cleaned_data.get("quantity")
        ]
        if not cleaned_forms:
            messages.error(request, "حداقل یک کالا باید وارد شود.")
            return render(request, self.template_name, {"formset": formset})

        try:
            with transaction.atomic():
                purchase = CustomerPurchase.objects.create(total_amount=0)
                total = 0

                # First pass: validate inventory for all items
                for f in cleaned_forms:
                    product = get_object_or_404(Product, product_id=f.cleaned_data["product_id"])
                    quantity = f.cleaned_data["quantity"]

                    inv = Inventory.objects.select_for_update().get(product=product)
                    if inv.quantity < quantity:
                        raise ValueError(f"موجودی کافی برای «{product.name}» وجود ندارد.")

                # Second pass: create items and decrement inventory
                for f in cleaned_forms:
                    product = get_object_or_404(Product, product_id=f.cleaned_data["product_id"])
                    quantity = f.cleaned_data["quantity"]
                    inv = Inventory.objects.select_for_update().get(product=product)

                    PurchaseItem.objects.create(
                        purchase=purchase,
                        product=product,
                        quantity=quantity,
                        price=product.price,
                    )
                    inv.quantity -= quantity
                    inv.save()
                    total += product.price * quantity

                purchase.total_amount = total
                purchase.save()

        except ValueError as e:
            messages.error(request, str(e))
            return render(request, self.template_name, {"formset": formset})
        except Inventory.DoesNotExist:
            messages.error(request, "برای برخی کالاها رکورد موجودی یافت نشد.")
            return render(request, self.template_name, {"formset": formset})

        return redirect("purchase_invoice", pk=purchase.cp_id)


class PurchaseInvoiceView(LoginRequiredMixin, DetailView):
    model = CustomerPurchase
    template_name = "purchase_invoice.html"
    context_object_name = "purchase"
    login_url = reverse_lazy("login")


