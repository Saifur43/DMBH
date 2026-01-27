from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

class User(AbstractUser):
    IS_ADMIN = 'admin'
    IS_BUYER = 'buyer'
    ROLE_CHOICES = (
        (IS_ADMIN, 'Admin'),
        (IS_BUYER, 'Buyer'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default=IS_BUYER)

    phone_number = models.CharField(max_length=20, blank=True, null=True)

    @property
    def is_buyer(self):
        return self.role == self.IS_BUYER

    @property
    def is_app_admin(self):
        return self.role == self.IS_ADMIN or self.is_staff

class Cart(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey('Product', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_price(self):
        return self.quantity * self.product.target_price

    def __str__(self):
        return f"{self.quantity} x {self.product.style_name}"

class Product(models.Model):
    CATEGORY_CHOICES = (
        ('Activewear', 'Activewear'),
        ('Blazer', 'Blazer'),
        ('Cargo Pants', 'Cargo Pants'),
        ('Casual Shirt', 'Casual Shirt'),
        ('Coat', 'Coat'),
        ('Denim Jeans', 'Denim Jeans'),
        ('Dress', 'Dress'),
        ('Dress Pants', 'Dress Pants'),
        ('Formal Shirt', 'Formal Shirt'),
        ('Hoodie', 'Hoodie'),
        ('Jacket', 'Jacket'),
        ('Joggers', 'Joggers'),
        ('Kids Wear', 'Kids Wear'),
        ('Pants', 'Pants'),
        ('Polo Shirt', 'Polo Shirt'),
        ('Puffy Vest', 'Puffy Vest'),
        ('Shirt', 'Shirt'),
        ('Shorts', 'Shorts'),
        ('Suit', 'Suit'),
        ('Sweater', 'Sweater'),
        ('Sweatshirt', 'Sweatshirt'),
        ('T-Shirt', 'T-Shirt'),
        ('Track Pants', 'Track Pants'),
        ('Vest', 'Vest'),
        ('Other', 'Other'),
    )

    code = models.CharField(max_length=50, unique=True)
    style_name = models.CharField(max_length=100)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    fabric_type = models.CharField(max_length=100)
    gsm = models.CharField(max_length=20, help_text="Grams per Square Meter")
    available_colors = models.CharField(max_length=200)
    size_range = models.CharField(max_length=100)
    moq = models.PositiveIntegerField(help_text="Minimum Order Quantity")
    target_price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Target Price per Unit")
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def main_image(self):
        """Get the main image or the first available image"""
        main = self.images.filter(is_main=True).first()
        if main:
            return main.image
        first = self.images.first()
        return first.image if first else None

    def __str__(self):
        return f"{self.style_name} ({self.code})"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='product_gallery/')
    is_main = models.BooleanField(default=False, help_text="Set as main display image")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image for {self.product.style_name}"

class Inquiry(models.Model):
    STATUS_CHOICES = (
        ('New', 'New'),
        ('Replied', 'Replied'),
        ('Closed', 'Closed'),
    )

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='inquiries')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='inquiries')
    requested_quantity = models.PositiveIntegerField()
    target_price = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='New')
    admin_reply = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Inquiry by {self.buyer.username} for {self.product.code}"

class SampleRequest(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Sent', 'Sent'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    )

    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='sample_requests')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sample_requests')
    sample_type = models.CharField(max_length=100, blank=True, null=True, help_text="e.g. Proto, Fit, PP")
    request_date = models.DateField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sample Request: {self.product.style_name}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Confirmed', 'Confirmed'),
        ('In Progress', 'In Progress'),
        ('Shipped', 'Shipped'),
        ('Completed', 'Completed'),
        ('Cancelled', 'Cancelled'),
    )

    order_number = models.CharField(max_length=50, unique=True)
    buyer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='orders')
    delivery_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_amount(self):
        return sum(item.total_price for item in self.items.all())

    def __str__(self):
        return f"Order #{self.order_number}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_price(self):
        qty = self.quantity if self.quantity else 0
        price = self.unit_price if self.unit_price else 0
        return qty * price

    def __str__(self):
        return f"{self.quantity} x {self.product.style_name} in {self.order.order_number}"
