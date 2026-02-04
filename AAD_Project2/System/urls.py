from django.urls import path , re_path
from django.urls.resolvers import URLPattern 
from django.views.generic import TemplateView 
from django.conf import settings 
from django.conf.urls.static import static
from .views import CustomLoginView , ProductDetailView , MultiPurchaseCreateView , PurchaseInvoiceView , AttendanceCreateView , ManagerAttendanceView , SalaryReportView , DebtListView , DebtUpdateView , InventoryListView , ProfitReportView , StoreManagerDashboardView , EmployeeDashboardView , AttendanceCheckView
app_name='system'

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("product/<uuid:pk>/", ProductDetailView.as_view(), name="product_detail"), 
    path("purchase/multi/", MultiPurchaseCreateView.as_view(), name="multi_purchase_create"), 
    path("purchase/invoice/<uuid:pk>/", PurchaseInvoiceView.as_view(), name="purchase_invoice"), 
    path('attendance/', AttendanceCheckView.as_view(), name='attendance_create'), 
    path('inventorylist/',InventoryListView.as_view(),name='inventory_list'),
    path('attendance/success/', TemplateView.as_view(template_name="attendance_success.html"), name='attendance_success'), 
    path('manager/attendance/', ManagerAttendanceView.as_view(), name='manager_attendance'), 
    path('salary-report/', SalaryReportView.as_view(), name='salary_report'), 
    path("debts/", DebtListView.as_view(), name="debt_list"), 
    path("debts/<uuid:pk>/update/", DebtUpdateView.as_view(), name="debt_update"), 
    path("profit/", ProfitReportView.as_view(), name="profit_report"), 
    path("manager/dashboard/", StoreManagerDashboardView.as_view(), name="storemanager_dashboard"), 
    path("employee/dashboard/", EmployeeDashboardView.as_view(), name='employee_dashboard'),
    ]
if settings.DEBUG: urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)