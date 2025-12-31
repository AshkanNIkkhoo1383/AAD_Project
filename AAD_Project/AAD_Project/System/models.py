from django.db import models 
from django.core.validators import MinLengthValidator, MaxLengthValidator
import uuid

class Person(models.Model):
    person_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=50, verbose_name="نام")
    last_name = models.CharField(max_length=50, verbose_name="نام خانوادگی")
    birth_date = models.DateField(verbose_name="تاریخ تولد")
    # جنسیت با انتخاب‌های مشخص
    GENDER_CHOICES = [('M', 'مرد'),('F', 'زن'),]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="جنسیت")
    phone_number = models.IntegerField(max_length=12,validators=[MinLengthValidator(12),MaxLengthValidator(12)],verbose_name="شماره تلفن",) 
    position = models.CharField(max_length=50, verbose_name="سمت شخص") 
    def __str__(self):
        return f"{self.first_name} {self.last_name}"
class Employee(Person): 
    position = models.CharField(max_length=50,default='employees', verbose_name="سمت شخص", editable=False) 
    photo = models.ImageField(upload_to='employees/', verbose_name="عکس کارمند", blank=True, null=True) 
    # کاری که انجام می‌دهد (با لیست انتخاب)
    JOB_CHOICES = [
        ('SELLER', 'فروشنده'),
        ('STOCK', 'انباردار'),
    ]
    job = models.CharField(max_length=20, choices=JOB_CHOICES, verbose_name="سمت")
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_job_display()}"
class Product(models.Model):
    product_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="اسم کالا")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت کالا")
    PRODUCT_TYPE_CHOICES = [
        ('WRITING', 'ابزار نوشتن'),
        ('PAPER', 'محصولات کاغذی'),
        ('ACCESSORY', 'لوازم جانبی'),
        ('STORAGE', 'وسایل نگهداری'), 
        ('OTHER', 'سایر'),
    ]
    product_type = models.CharField(max_length=20, choices=PRODUCT_TYPE_CHOICES, verbose_name="نوع کالا")
    photo = models.ImageField(upload_to='products/', verbose_name="عکس کالا", blank=True, null=True)
    def __str__(self):
        return f"{self.name} - {self.get_product_type_display()}"
class Inventory(models.Model):
    inventory_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    # ارتباط با کالا
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name="کالا")
    # تعداد موجودی
    quantity = models.PositiveIntegerField(verbose_name="تعداد موجودی")
    # تاریخ آخرین بروزرسانی
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")
    def __str__(self):
        return f"{self.product.name} - موجودی: {self.quantity}"
class CustomerPurchase(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase_date = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ خرید")
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مجموع خرید",null=True)
    # رابطه چندبه‌چند با کالا از طریق مدل واسط PurchaseItem
    products = models.ManyToManyField(Product, through='PurchaseItem', verbose_name="کالاهای خریداری‌شده")
    def __str__(self):
        return f"خرید {self.customer} در تاریخ {self.purchase_date.strftime('%Y-%m-%d')} - مجموع: {self.total_amount}"
class PurchaseItem(models.Model):
    pi_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    purchase = models.ForeignKey('CustomerPurchase', on_delete=models.CASCADE, related_name="items", verbose_name="خرید")
    product = models.ForeignKey('Product', on_delete=models.CASCADE, verbose_name="کالا")
    quantity = models.PositiveIntegerField(verbose_name="تعداد")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="قیمت واحد")

    def get_total_price(self):
        return self.quantity * self.price

    def __str__(self):
        return f"{self.product.name} × {self.quantity} (خرید: {self.purchase.id})"
class SpecialCustomer(Person):
    address = models.CharField(max_length=255, verbose_name="آدرس")
    position = models.CharField(max_length=50,default='specialcustomer', verbose_name="سمت شخص", editable=False) 
    def __str__(self):
        return f"مشتری ویژه: {self.first_name} {self.last_name}"
class Credit(models.Model):
    credit_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    customer = models.ForeignKey(SpecialCustomer,on_delete=models.CASCADE,related_name="credits",verbose_name="مشتری ویژه")
    total_debt = models.DecimalField(max_digits=12,decimal_places=2,verbose_name="مجموع بدهی")
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده؟")
    purchase = models.OneToOneField(CustomerPurchase,on_delete=models.CASCADE,related_name="credit",verbose_name="خرید مرتبط")
    def __str__(self):
        status = "پرداخت شده" if self.is_paid else "بدهکار"
        return f"نسیه مشتری {self.customer} - مجموع بدهی: {self.total_debt} ({status})"
class Creditor(models.Model):
    creditor_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100, verbose_name="نام طلبکار")
    creditor_type_choices = [
        ('PERSON', 'فرد'),
        ('COMPANY', 'شرکت'),
        ('SHOP', 'مغازه'),
    ]
    creditor_type = models.CharField(
        max_length=10,
        choices=creditor_type_choices,
        verbose_name="نوع طلبکار"
    )
    phone_number = models.CharField(max_length=15, verbose_name="شماره تماس")
    address = models.CharField(max_length=255, verbose_name="آدرس")

    def __str__(self):
        return f"{self.name} ({self.get_creditor_type_display()})"
class Debt(models.Model):
    debt_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    creditor = models.ForeignKey(
        Creditor,
        on_delete=models.CASCADE,
        related_name="debts",
        verbose_name="طلبکار"
    )
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ بدهی")
    due_date = models.DateField(verbose_name="تاریخ سررسید")
    is_paid = models.BooleanField(default=False, verbose_name="پرداخت شده؟")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات بدهی")

    def __str__(self):
        status = "پرداخت شده" if self.is_paid else "بدهی معوق"
        return f"بدهی به {self.creditor.name} - مبلغ: {self.amount} ({status})"
