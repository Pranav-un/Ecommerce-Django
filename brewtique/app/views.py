import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Count
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views import View
from . models import Cart, Customer, Order, OrderItem, Product
from . forms import CustomerProfileForm, CustomerRegistrationForm
from django.http import JsonResponse

# Create your views here.
def home(request):
  return render(request, "app/home.html")

def about(request):
  return render(request, "app/about.html")

def contact(request):
  return render(request, "app/contact.html")

# class CategoryView(View):
#   def get(self,request,val):
#     product = Product.objects.filter(category=val)
#     title = Product.objects.filter(category=val).values('title')
#     return render(request,"app/category.html",locals())
  
class CategoryView(View):
  def get(self, request, val):
      products = Product.objects.filter(category=val)  # Fetch products based on category
      category_name = val  # To pass the category name to the template
      return render(request, "app/category.html", {'products': products, 'category_name': category_name})
  
# class ProductDetails(View):
#    def get(self,request,pk):
#       products = Product.objects.get(pk=pk)
#       return render(request,"app/productdetail.html",locals())
   
class ProductDetails(View):
  def get(self, request, pk):
      product = get_object_or_404(Product, pk=pk)  # Use get_object_or_404 to handle non-existent products
      return render(request, "app/productdetail.html", {'product': product})  # Pass the product to the template
  
class HomePageView(View):
    def get(self, request):
        products = Product.objects.all()  # Fetch all products
        return render(request, "app/home.html", {'products': products})
    
class CustomerRegistrationView(View):
   def get (self,request):
      form = CustomerRegistrationForm()
      return render(request, 'app/customerregistration.html', locals())
   def post(self, request):
      form = CustomerRegistrationForm(request.POST)
      if form.is_valid():
         form.save()
         messages.success(request,"Registration Successfull")
      else:
          messages.warning(request,"Invalid Input Data")   
      return render(request, 'app/customerregistration.html', locals())

class ProfileView(View):
   def get(self,request):
      form = CustomerProfileForm()
      return render(request, 'app/profile.html', locals())
   def post(self,request):
       form = CustomerProfileForm(request.POST)
       if form.is_valid():
        user = request.user
        name = form.cleaned_data['name']  
        locality = form.cleaned_data['locality']
        city = form.cleaned_data['city']
        mobile = form.cleaned_data['mobile']
        state = form.cleaned_data['state']
        zipcode = form.cleaned_data['zipcode']

        reg = Customer(user=user, name=name, locality=locality, mobile=mobile, city=city, state=state, zipcode=zipcode)
        reg.save() 
        messages.success(request,"Saved")
       else:
          messages.warning(request,"Invalid Input Data")
       return render(request, 'app/profile.html', locals())
   
def address(request):
   add = Customer.objects.filter(user = request.user)
   return render(request, 'app/address.html',locals())

class updateAddress(View):
      def get(self, request, pk):
         add = Customer.objects.get(pk=pk)
         form = CustomerProfileForm(instance=add)
         return render(request, 'app/updateAddress.html',locals())
      def post(self, request, pk):
         form = CustomerProfileForm(request.POST)
         if form.is_valid():
          add = Customer.objects.get(pk=pk)
          add.name = form.cleaned_data['name']
          add.locality = form.cleaned_data['locality']
          add.city = form.cleaned_data['city']
          add.mobile = form.cleaned_data['mobile']
          add.state = form.cleaned_data['state']
          add.zipcode = form.cleaned_data['zipcode']
          add.save()
          messages.success(request,"Profile has been Updated")
         else:
          messages.warning(request,"Invalid Input Data") 
         return redirect("address")   
         
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, Product

@login_required
def add_to_cart(request):
    # Get the product ID from the request
    prod_id = request.GET.get('prod_id')
    
    if prod_id:
        try:
            # Get the product object
            product = Product.objects.get(id=prod_id)
            user = request.user

            # Check if the product is already in the user's cart
            existing_cart_item = Cart.objects.filter(user=user, product=product).first()

            if existing_cart_item:
                # If the product is already in the cart, increase the quantity
                existing_cart_item.quantity += 1
                existing_cart_item.save()
            else:
                # If the product is not in the cart, add it
                Cart.objects.create(user=user, product=product, quantity=1)

            # Redirect to cart page (or wherever you want)
            return redirect('showcart')

        except Product.DoesNotExist:
            # If the product doesn't exist, redirect to the homepage
            return redirect('home')
    
    # If no product ID is provided, redirect to homepage
    return redirect('home')


def show_cart(request):
    user = request.user
    cart = Cart.objects.filter(user=user)
    amount = 0
    shipping_amount = 40  # Example fixed shipping cost
    cart_items = []
    
    for item in cart:
        total_item_cost = item.quantity * item.product.discounted_price
        amount += total_item_cost
        cart_items.append({
            'id': item.id,
            'product': item.product,
            'quantity': item.quantity,
            'total_cost': total_item_cost,
        })
    
    total_amount = amount + shipping_amount

    return render(request, 'app/addtocart.html', {
        'cart_items': cart_items,
        'total_amount': total_amount,
        'shipping_amount': shipping_amount,
        'amount': amount
    })

def update_cart_quantity(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_id = data.get('cart_id')
        quantity = int(data.get('quantity'))
        
        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            cart_item.quantity = quantity
            cart_item.save()

            total_item_cost = cart_item.quantity * cart_item.product.discounted_price
            return JsonResponse({'success': True, 'total_cost': total_item_cost})
        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'})

def remove_cart_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        cart_id = data.get('cart_id')

        try:
            cart_item = Cart.objects.get(id=cart_id, user=request.user)
            cart_item.delete()
            return JsonResponse({'success': True})
        except Cart.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Item not found'})
        

class ConfirmOrderView(View):
    def get(self, request):
        # Get user's addresses from the Customer model
        addresses = Customer.objects.filter(user=request.user)
        
        # Get cart items for the user (you can adjust as per your cart logic)
        cart_items = Cart.objects.filter(user=request.user)
        
        # If the user doesn't have any items in the cart, redirect them to the cart page
        if not cart_items:
            messages.warning(request, "Your cart is empty!")
            return redirect('showcart')

        # Display the confirm order page with addresses and cart items
        return render(request, 'app/confirm_order.html', {
            'addresses': addresses,
            'cart_items': cart_items
        })

    def post(self, request):
        # Handle form submission for confirming the order with selected address
        address_id = request.POST.get('address')  # The selected address id
        if not address_id:
            messages.warning(request, "Please select an address")
            return redirect('confirm-order')  # Redirect back to the confirm order page
        
        try:
            selected_address = Customer.objects.get(id=address_id, user=request.user)
        except Customer.DoesNotExist:
            messages.error(request, "Selected address not found.")
            return redirect('confirm-order')

        # Here you can save the order details, e.g., create an order object
        # Assuming you have an Order model, you can save the order like this:
        # order = Order(user=request.user, address=selected_address, ...)
        # order.save()

        # Clear the user's cart (if necessary)
        Cart.objects.filter(user=request.user).delete()
        
        # Show success message and redirect
        messages.success(request, "Your order has been placed successfully!")
        return redirect('order-summary')  # You can redirect to an order summary page
    
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Cart, Order, OrderItem

from django.shortcuts import render
from .models import Order

def confirm_order(request):
    # Assume user is logged in and there's an order for the user
    order = Order.objects.filter(user=request.user).last()  # Or any other way to fetch the order
    return render(request, 'app/confirm_order.html', {'order': order})




# View for Order Success


def create_order(request):
    user = request.user
    cart_items = Cart.objects.filter(user=user)
    
    # Get user address
    customer = Customer.objects.filter(user=user).first()

    # Calculate total amount
    total_amount = sum(item.product.discounted_price * item.quantity for item in cart_items)
    
    # Create Order
    order = Order.objects.create(
        user=user,
        shipping_address=customer,
        total_amount=total_amount,
        payment_method=request.POST['payment_method'],
        status='PENDING'
    )
    
    # Create Order Items
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.discounted_price
        )
        
    # Clear the cart after order
    cart_items.delete()

    # Redirect to order confirmation page
    return redirect('order_confirmation', order_id=order.id)


def order_confirmation(request, order_id):
    order = Order.objects.get(id=order_id)
    order_items = OrderItem.objects.filter(order=order)
    
    return render(request, 'app/order_confirmation.html', {
        'order': order,
        'order_items': order_items,
    })

def process_payment(request, order_id):
    order = Order.objects.get(id=order_id)
    
    # Payment gateway integration goes here (e.g., Razorpay, PayPal, etc.)
    payment_successful = True  # This should be the response from the payment gateway
    
    if payment_successful:
        order.payment_status = 'PAID'
        order.status = 'SHIPPED'  # Or change based on your logic
        order.save()
    
    return redirect('order_success', order_id=order.id)




class AdminOrderListView(View):
    def get(self, request):
        orders = Order.objects.all().order_by('-order_date')
        return render(request, 'app/admin_order_list.html', {'orders': orders})


def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST['status']
        order.status = new_status
        order.save()
        return redirect('admin_order_list')
    
    return render(request, 'app/update_order_status.html', {'order': order})


def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id)
    
    if order.status == 'PENDING':
        order.status = 'CANCELLED'
        order.save()
        # Optionally, add logic to reverse payments, etc.
    
    return redirect('order_success', order_id=order.id)


def update_order_status(request, order_id):
    order = Order.objects.get(id=order_id)
    
    if request.method == 'POST':
        new_status = request.POST['status']
        order.status = new_status
        order.save()
        return redirect('admin_order_list')
    
    return render(request, 'app/update_order_status.html', {'order': order})



def order_details(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)
    return render(request, 'app/order_details.html', {'order': order})



def user_order_list(request):
    orders = Order.objects.filter(user=request.user).order_by('-order_date')
    return render(request, 'app/user_orders.html', {'orders': orders})

def place_order(request):
    # Fetch the user's cart items
    cart_items = Cart.objects.filter(user=request.user)
    
    # Calculate the total amount for the order
    total_amount = sum(item.total_cost for item in cart_items)
    
    if total_amount <= 0:
        return redirect('cart')  # If no items in cart, redirect back to cart page
    
    # Create the order
    order = Order.objects.create(
        user=request.user,
        total_amount=total_amount,
        status='PENDING',
        payment_method=request.POST.get('payment_method', 'cash_on_delivery'),  # Default to 'cash_on_delivery' if missing
    )
    
    # Create order items for each cart item
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.discounted_price,
        )

    # Optionally, clear the user's cart after placing the order
    cart_items.delete()

    # Redirect to order success with the order_id
    return redirect('order_success', order_id=order.id)


def get_cart_items(request):
    cart_items = Cart.objects.filter(user=request.user)
    return cart_items

def calculate_total_amount(cart_items):
    total = 0
    for item in cart_items:
        total += item.product.discounted_price * item.quantity  # Multiply product price by quantity
    return total


def calculate_shipping(cart_items):
    # For now, let's assume a fixed shipping fee of ₹50
    return 50



def confirm_order(request):
    # Assume you have logic to get or create an order
    order_id = request.session.get('order_id')  # Or however you manage order IDs
    order = get_object_or_404(Order, id=order_id)  # Ensure you fetch the order

    # Calculate amounts or any other logic needed
    cart_items = get_cart_items(request)  # Assuming this function fetches cart items
    total_amount = calculate_total_amount(cart_items)
    shipping_amount = calculate_shipping(cart_items)

    return render(request, 'app/confirm_order.html', {
        'order': order,
        'amount': total_amount,
        'shipping_amount': shipping_amount,
        'total_amount': total_amount + shipping_amount,
        'cart_items': cart_items,
    })

from django.shortcuts import redirect, get_object_or_404
from .models import Cart, Order, OrderItem, Customer

def create_order(request):
    if request.method == 'POST':
        user = request.user
        payment_method = request.POST.get('payment_method')

        # Fetch cart items
        cart_items = Cart.objects.filter(user=user)
        
        if not cart_items.exists():
            messages.warning(request, "Your cart is empty!")
            return redirect('showcart')

        # Get user address (assuming you have a way to get it)
        customer = Customer.objects.filter(user=user).first()
        total_amount = sum(item.total_cost for item in cart_items)

        # Create the order
        order = Order.objects.create(
            user=user,
            total_amount=total_amount,
            payment_method=payment_method,
            shipping_address=customer,
            status='PENDING'
        )

        # Create order items
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.discounted_price,
            )

        # Clear the cart after order
        cart_items.delete()

        # Redirect to order success page
       # return redirect('order_success')

    return redirect('home')  # Redirect if not a POST request



def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)  # Ensure the order belongs to the user
    return render(request, 'app/order_success.html', {'order': order})

# views.py
from django.shortcuts import render
from .models import Customer, Cart
from django.contrib.auth.decorators import login_required

def confirm_order(request):
    # Get all customer (address) instances for the logged-in user
    addresses = Customer.objects.filter(user=request.user)

    # Fetch cart items for the logged-in user
    cart_items = Cart.objects.filter(user=request.user)

    # Calculate subtotal (total of all cart items)
    amount = sum(item.total_cost for item in cart_items)

    # Example values for shipping (you can adjust as needed)
    shipping_amount = 40  # Shipping cost
    total_amount = amount + shipping_amount

    # Optional: Update the order total in the database if an order is placed
    # You would save the order in the database here after the user confirms

    return render(request, 'app/confirm_order.html', {
        'addresses': addresses,
        'cart_items': cart_items,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': total_amount,
    })

# views.py
from django.shortcuts import redirect
from .models import Order, Cart, Customer

# views.py
from django.shortcuts import render, redirect
from .models import Cart, Customer, Order
from django.contrib.auth.decorators import login_required

def create_order(request):
    if request.method == 'POST':
        # Get the selected address and payment method from the POST request
        address_id = request.POST.get('address')
        payment_method = request.POST.get('payment_method')
        
        # Ensure the address exists
        try:
            shipping_address = Customer.objects.get(id=address_id)
        except Customer.DoesNotExist:
            return redirect('address')  # Handle the error as needed

        # Calculate total amount from the cart
        cart_items = Cart.objects.filter(user=request.user)
        subtotal = sum(item.total_cost for item in cart_items)
        shipping_amount = 40  # Assuming a fixed shipping cost
        total_amount = subtotal + shipping_amount

        # Create the order
        order = Order.objects.create(
            user=request.user,
            payment_method=payment_method,
            shipping_address=shipping_address,
            total_amount=total_amount,
        )

        # Update the cart items
        for item in cart_items:
            item.is_ordered = True
            item.order = order
            item.save()

        # Pass the total_amount to the frontend
        return redirect('order-success', order_id=order.id)

    return render(request, 'app/order_summary.html')

def order_success(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return redirect('home')  # Or show an error message

    return render(request, 'app/order_success.html', {'order': order})

def confirm_order(request):
    addresses = Customer.objects.filter(user=request.user)
    cart_items = Cart.objects.filter(user=request.user)

    # Calculate subtotal (total of all cart items)
    amount = sum(item.total_cost for item in cart_items)

    # Shipping cost
    shipping_amount = 40
    total_amount = amount + shipping_amount

    # Pass these variables to the template
    return render(request, 'app/confirm_order.html', {
        'addresses': addresses,
        'cart_items': cart_items,
        'amount': amount,
        'shipping_amount': shipping_amount,
        'total_amount': total_amount,
    })

