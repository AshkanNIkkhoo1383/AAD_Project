from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.views import LoginView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin 
from django.views.generic.detail import DetailView 
from django.views.generic import CreateView , ListView , UpdateView , FormView , TemplateView
from django.urls import reverse_lazy
from .models import CustomUser , Product ,Inventory, CustomerPurchase, PurchaseItem , Attendance , Debt , Employee
from .forms import PurchaseItemFormSet , AttendanceForm , DateRangeForm
from django.contrib import messages
from django.db import transaction 
from django.views import View 
from datetime import timedelta,datetime
from django.utils import timezone

class CustomLoginView(LoginView):
    template_name = "login.html"   # قالب صفحه ورود
    redirect_authenticated_user = True

    def get_success_url(self):
        user = self.request.user
        # بررسی نقش کاربر
        if user.position == "storemanager":
            return reverse_lazy("system:storemanager_dashboard")  # صفحه مدیر فروشگاه
        else:
            return reverse_lazy('system:employee_dashboard')      # صفحه کارمند
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

        return redirect("system:purchase_invoice", pk=purchase.cp_id)
class PurchaseInvoiceView(LoginRequiredMixin, DetailView):
    model = CustomerPurchase
    template_name = "purchase_invoice.html"
    context_object_name = "purchase"
    login_url = reverse_lazy("login")
class InventoryListView(LoginRequiredMixin,ListView):
    model = Inventory
    template_name = 'inventory_list.html'  # مسیر قالب HTML
    context_object_name = 'inventories'  # نامی که در قالب استفاده می‌کنی
    login_url = reverse_lazy("login")
class AttendanceCreateView(LoginRequiredMixin,CreateView):
    model = Attendance
    form_class = AttendanceForm
    template_name = 'attendance_form.html'
    success_url = reverse_lazy('system:storemanager_dashboard')
    login_url = reverse_lazy("login") 

    def form_valid(self, form):
        # فرض: کارمند از کاربر لاگین شده گرفته می‌شود
        form.instance.employee = self.request.user.employee  
        return super().form_valid(form)
class ManagerAttendanceView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Attendance
    template_name = 'manager_attendance.html'
    context_object_name = 'attendances'
    login_url = reverse_lazy("login")
    # فقط مدیر فروشگاه اجازه دسترسی دارد
    def test_func(self):
        return self.request.user.position == "storemanager"

    # فقط رکوردهای امروز و تایید نشده
    def get_queryset(self):
        today = datetime.date.today()
        return Attendance.objects.filter(date=today, approved_by_manager=False)

    def post(self, request, *args, **kwargs):
        approved_ids = request.POST.getlist('approve')
        Attendance.objects.filter(attendance_id__in=approved_ids).update(approved_by_manager=True)
        return redirect('system:storemanager_dashboard') 
class SalaryReportView(LoginRequiredMixin, UserPassesTestMixin, View):
    template_name = "salary_report.html"
    login_url = reverse_lazy("login")
    def test_func(self):
        return self.request.user.position == "storemanager"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        hourly_rate = float(request.POST.get('hourly_rate'))

        attendances = Attendance.objects.filter(
            date__range=[start_date, end_date],
            approved_by_manager=True
        )

        report = {}
        for att in attendances:
            if att.check_in and att.check_out:
                duration = datetime.combine(att.date, att.check_out) - datetime.combine(att.date, att.check_in)
                hours = duration.total_seconds() / 3600
                emp = att.employee
                if emp not in report:
                    report[emp] = {'hours': 0}
                report[emp]['hours'] += hours

        for emp in report:
            report[emp]['salary'] = round(report[emp]['hours'] * hourly_rate, 2)

        return render(request, self.template_name, {
            'report': report,
            'start_date': start_date,
            'end_date': end_date,
            'hourly_rate': hourly_rate
        })
class DebtListView(LoginRequiredMixin, UserPassesTestMixin, ListView):
    model = Debt
    template_name = "debt_list.html"
    context_object_name = "debts"

    def test_func(self):
        return self.request.user.position == "storemanager"  # فقط کاربر مدیر
    def get_queryset(self): 
        return Debt.objects.filter(is_paid=False).select_related('creditor')
class DebtUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Debt
    fields = ['is_paid']
    template_name = "debt_update.html"
    success_url = reverse_lazy("system:storemanager_dashboard")

    def test_func(self):
        return self.request.user.position == "storemanager"
class ProfitReportView(LoginRequiredMixin, UserPassesTestMixin, FormView):
    template_name = "profit_report.html"
    form_class = DateRangeForm

    def test_func(self):
        return self.request.user.position == "storemanager"

    def form_valid(self, form):
        start = form.cleaned_data['start_date']
        end = form.cleaned_data['end_date']
        paid_debts = Debt.objects.filter(is_paid=True, due_date__range=(start, end))
        total_income = sum(d.amount for d in paid_debts)
        profit = total_income * 0.25
        return self.render_to_response(self.get_context_data(
            form=form,
            total_income=total_income,
            profit=profit,
            start=start,
            end=end,
            debts=paid_debts
        ))
class StoreManagerDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "storemanager_dashboard.html"

    def test_func(self):
        return self.request.user.position == "storemanager"
class EmployeeDashboardView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "employee_dashboard.html"

    def test_func(self):
        return self.request.user.position == "employees"
class AttendanceCheckView(View):
    template_name = "attendance_form.html"
    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        employee_id = request.POST.get("employee_id")
        action = request.POST.get("action")  # check_in یا check_out

        try:
            employee = Employee.objects.get(person_id=employee_id)
        except Employee.DoesNotExist:
            return render(request, self.template_name, {
                "message": "کارمند با این شناسه یافت نشد."
            })

        now = timezone.localtime()
        today = now.date()

        attendance, created = Attendance.objects.get_or_create(
            employee=employee,
            date=today,
            defaults={"status": "PRESENT"}
        )

        # ثبت ورود
        if action == "check_in":
            if attendance.check_in:
                return render(request, self.template_name, {
                    "message": "ورود امروز قبلاً ثبت شده است."
                })

            attendance.check_in = now.time()
            attendance.status = "PRESENT"
            attendance.save()

            return render(request, self.template_name, {
                "message": f"ورود {employee.first_name} {employee.last_name} با موفقیت ثبت شد."
            })

        # ثبت خروج
        if action == "check_out":
            if not attendance.check_in:
                return render(request, self.template_name, {
                    "message": "ابتدا باید ورود ثبت شود."
                })

            if attendance.check_out:
                return render(request, self.template_name, {
                    "message": "خروج امروز قبلاً ثبت شده است."
                })

            attendance.check_out = now.time()
            attendance.save()

            return render(request, self.template_name, {
                "message": f"خروج {employee.first_name} {employee.last_name} با موفقیت ثبت شد."
            })

        return render(request, self.template_name, {"message": "درخواست نامعتبر"})
