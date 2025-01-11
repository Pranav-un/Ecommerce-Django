from django.db import models
from django.contrib.auth.models import User
from django.db import models

# Choices for product categories
STATE_CHOICES = (
    ('Kerala', 'Kerala'),
    ('TamilNadu', 'TamilNadu')
)


CATEGORY_CHOICES = (
    ('TE', 'Tea'),
    ('CE', 'Coffee'),
    ('SN', 'Snacks'),  
    ('GF', 'Gifts'),
)

class Product(models.Model):
    title = models.CharField(max_length=200, verbose_name="Product Title")  
    selling_price = models.FloatField(null=True, blank=True,verbose_name="Selling Price")  
    discounted_price = models.FloatField(null=True, blank=True, verbose_name="Discounted Price")
    description = models.TextField(verbose_name="Product Description")  
    composition = models.TextField(null=True, blank=True, verbose_name="Composition") 
    prod_app = models.TextField(null=True, blank=True, verbose_name="Product Application")  
    category = models.CharField(choices=CATEGORY_CHOICES, max_length=20, verbose_name="Product Category")  
    product_image = models.ImageField(upload_to='product', null=True, blank=True, verbose_name="Product Image")  
    stock = models.CharField(max_length=20, choices=[('available', 'Available'), ('not available', 'Not Available')], default='available', verbose_name="Stock Status")

    def __str__(self):
        return self.title
    

class Customer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    locality = models.CharField(max_length=200)
    city = models.CharField(max_length=100)
    mobile = models.IntegerField()
    zipcode = models.IntegerField()
    state = models.CharField(choices=STATE_CHOICES, max_length=100)
    

    def __str__(self):
        return self.name
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    @property
    def total_cost(self):
        return self.quantity * self.product.discounted_price
    
    
    class Meta:
        unique_together = ('user', 'product')

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SHIPPED', 'Shipped'),
        ('DELIVERED', 'Delivered'),
        ('CANCELLED', 'Cancelled'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=ORDER_STATUS_CHOICES, default='PENDING')
    payment_method = models.CharField(max_length=50)
    payment_status = models.CharField(max_length=20, default='PENDING')
    shipping_address = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    total_amount = models.FloatField()

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='order_items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField()
    price = models.FloatField()

    def __str__(self):
        return f"{self.quantity} x {self.product.title}"
    



