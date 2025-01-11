

from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_view
from .forms import LoginForm, MyPasswordResetForm, MyPasswordChangeForm, MySetPasswordForm

urlpatterns = [
    path('', views.HomePageView.as_view(), name='home'),
    path('home/',views.about,name='home'),
    path('about/',views.about,name='about'),
    path('contact/',views.contact,name='contact'),
    path('category/<slug:val>/', views.CategoryView.as_view(), name='category'),
    path('product-detail/<int:pk>', views.ProductDetails.as_view(), name='product-detail'), 
    path('profile/',views.ProfileView.as_view(), name='profile'), 
    path('address/',views.address, name='address'), 
    path('updateAddress/<int:pk>',views.updateAddress.as_view(), name='updateAddress'), 
    path('add-to-cart/',views.add_to_cart, name='add-to-cart'),
    # path(' checkout/', views.checkout.as_view , name ='checkout'),
    path('cart/', views.show_cart, name='showcart'),
    path('update-cart/', views.update_cart_quantity, name='update-cart'),
    path('remove-cart-item/', views.remove_cart_item, name='remove-cart-item'),
    path('confirm-order/', views.ConfirmOrderView.as_view(), name='confirm-order'),
     path('confirm-order/', views.confirm_order, name='confirm-order'),
    
    # Order Success page
    path('order-success/', views.order_success, name='order-success'),

    path('create-order/', views.create_order, name='create_order'),
    path('order/confirmation/<int:order_id>/', views.order_confirmation, name='order_confirmation'),
    path('order/payment/<int:order_id>/', views.process_payment, name='process_payment'),
    
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/order/status/<int:order_id>/', views.update_order_status, name='update_order_status'),
    path('order/cancel/<int:order_id>/', views.cancel_order, name='cancel_order'),
    path('order-success/<int:order_id>/', views.order_success, name='order-success'),
    path('admin/orders/', views.AdminOrderListView.as_view(), name='admin_order_list'),
    path('admin/order/update/<int:order_id>/', views.update_order_status, name='update-order-status'),
    path('admin/order/cancel/<int:order_id>/', views.cancel_order, name='cancel-order'),
    path('orders/', views.user_order_list, name='user_order_list'),
    path('orders/<int:order_id>/', views.order_details, name='order_details'),
    path('orders/', views.user_order_list, name='user_order_list'),
    path('order-success/<int:order_id>/', views.order_success, name='order-success'),
    


    
      
      #lgoin
      path('registration/',views.CustomerRegistrationView.as_view(),name='customerregistration'),
      path('accounts/login/',auth_view.LoginView.as_view(template_name='app/login.html',authentication_form=LoginForm) , name='login'),
      path('passwordchange/', auth_view.PasswordChangeView.as_view(template_name='app/changepassword.html', form_class=MyPasswordChangeForm, success_url ='/passwordchangedone'),name = 'passwordchange'),
      path('passwordchangedone/', auth_view.PasswordChangeDoneView.as_view(template_name='app/passwordchangedone.html'),name = 'passwordchangedone'),
      path('logout/', auth_view.LogoutView.as_view(next_page='login'), name='logout'),
      path('password-reset/', auth_view.PasswordResetView.as_view(template_name='app/password_reset.html', form_class=MyPasswordResetForm), name='password_reset'),
      path('password-reset/done/', auth_view.PasswordResetDoneView.as_view(template_name='app/password_reset_done.html'), name="password_reset_done"),
      path('password-reset-confirm/<uidb64>/<token>/', auth_view.PasswordResetConfirmView.as_view(template_name='app/password_reset_confirm.html', form_class=MySetPasswordForm), name='password_reset_confirm'),
      path('password-reset-complete/', auth_view.PasswordResetCompleteView.as_view(template_name='app/password_reset_complete.html'), name='password_reset_complete'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)  # Serve media files


