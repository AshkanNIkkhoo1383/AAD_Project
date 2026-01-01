from django.urls import path , re_path
from django.urls.resolvers import URLPattern 
from .views import CustomLoginView , ProductDetailView , MultiPurchaseCreateView , PurchaseInvoiceView
app_name='system'

urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="login"),
    path("product/<uuid:pk>/", ProductDetailView.as_view(), name="product_detail"), 
    path("purchase/multi/", MultiPurchaseCreateView.as_view(), name="multi_purchase_create"), 
    path("purchase/invoice/<uuid:pk>/", PurchaseInvoiceView.as_view(), name="purchase_invoice"),
    ]
