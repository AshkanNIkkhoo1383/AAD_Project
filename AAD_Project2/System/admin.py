from django.contrib import admin
from .models import (
    Employee, Product, Inventory,
    CustomerPurchase, PurchaseItem, SpecialCustomer,
    Credit, Creditor, Debt, Wholesaler ,
    WholesalePurchase, WholesalePurchaseItem,
    StoreManager, CustomUser,
    StoreManagerProfile, EmployeeProfile,
    Attendance
)

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "job", "position")
    list_filter = ("job",)
    search_fields = ("first_name", "last_name")

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "product_type")
    list_filter = ("product_type",)
    search_fields = ("name",)

@admin.register(Inventory)
class InventoryAdmin(admin.ModelAdmin):
    list_display = ("product", "quantity", "updated_at")
    list_filter = ("updated_at",)

class PurchaseItemInline(admin.TabularInline):
    model = PurchaseItem
    extra = 1

@admin.register(CustomerPurchase)
class CustomerPurchaseAdmin(admin.ModelAdmin):
    list_display = ("purchase_date", "total_amount")
    inlines = [PurchaseItemInline]

@admin.register(SpecialCustomer)
class SpecialCustomerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "address", "phone_number")

@admin.register(Credit)
class CreditAdmin(admin.ModelAdmin):
    list_display = ("customer", "total_debt", "is_paid", "purchase")
    list_filter = ("is_paid",)

@admin.register(Creditor)
class CreditorAdmin(admin.ModelAdmin):
    list_display = ("name", "creditor_type", "phone_number", "address")
    list_filter = ("creditor_type",)
    search_fields = ("name", "phone_number")

@admin.register(Debt)
class DebtAdmin(admin.ModelAdmin):
    list_display = ("creditor", "amount", "due_date", "is_paid")
    list_filter = ("is_paid", "due_date")

@admin.register(Wholesaler)
class WholesalerAdmin(admin.ModelAdmin):
    list_display = ("name", "phone_number", "address")
    search_fields = ("name", "phone_number")

class WholesalePurchaseItemInline(admin.TabularInline):
    model = WholesalePurchaseItem
    extra = 1

@admin.register(WholesalePurchase)
class WholesalePurchaseAdmin(admin.ModelAdmin):
    list_display = ("wholesaler", "purchase_date", "total_amount")
    inlines = [WholesalePurchaseItemInline]
    search_fields = ("wholesaler__name",)
    list_filter = ("purchase_date",)

@admin.register(WholesalePurchaseItem)
class WholesalePurchaseItemAdmin(admin.ModelAdmin):
    list_display = ("purchase", "product", "quantity", "price", "get_total_price")
    search_fields = ("product__name",)

@admin.register(StoreManager)
class StoreManagerAdmin(admin.ModelAdmin):
    list_display = ("first_name", "last_name", "position")
    search_fields = ("first_name", "last_name")

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "position", "is_staff", "is_active")
    list_filter = ("position", "is_staff", "is_active")
    search_fields = ("username", "email")

@admin.register(StoreManagerProfile)
class StoreManagerProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "manager", "office_number")
    search_fields = ("user__username", "manager__first_name", "manager__last_name")

@admin.register(EmployeeProfile)
class EmployeeProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "employee")
    search_fields = ("user__username", "employee__first_name", "employee__last_name")

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ("employee", "date", "status", "check_in", "check_out", "approved_by_manager")
    list_filter = ("status", "approved_by_manager", "date")
    search_fields = ("employee__first_name", "employee__last_name")
