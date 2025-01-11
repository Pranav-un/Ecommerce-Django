from django.contrib import admin
from .models import Product
from django.utils.html import mark_safe
from . models import Customer, Cart

class ProductModelAdmin(admin.ModelAdmin):
    # Specify the fields to display in the admin list view
    list_display = ('title', 'selling_price', 'discounted_price', 'category', 'image_tag')

    # Method to display the product image in the admin list view
    def image_tag(self, obj):
        if obj.product_image:
            return mark_safe(f'<img src="{obj.product_image.url}" style="width: 50px; height: auto;" />')
        return "No Image"
    
    image_tag.short_description = 'Image'  # Column name in the admin list

# Register the Product model with the custom admin model
admin.site.register(Product, ProductModelAdmin)

@admin.register(Customer)
class CustomerModelAdmin(admin.ModelAdmin):
     list_display = ('id', 'user','locality', 'city', 'state' ,'zipcode')

@admin.register(Cart)
class CustomerModelAdmin(admin.ModelAdmin):
     list_display = ('id', 'user', 'product', 'quantity')


# admin.py
from django.contrib import admin
from .models import Order, OrderItem

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 1

class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'payment_status', 'order_date', 'total_amount')
    list_filter = ('status', 'payment_status')
    inlines = [OrderItemInline]

admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem)


