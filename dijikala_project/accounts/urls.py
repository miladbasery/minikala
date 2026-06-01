from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/customer/', views.signup_customer, name='signup_customer'),
    path('signup/seller/', views.signup_seller, name='signup_seller'),
    path('login/', auth_views.LoginView.as_view(template_name='accounts/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('profile/', views.profile_view, name='profile'),
    path('profile/delete/', views.delete_account, name='delete_account'),
    path('user/<int:user_id>/', views.public_profile, name='public_profile'),
    path('about/', views.about_us, name='about_us'),
    path('terms/', views.terms, name='terms'),

]
