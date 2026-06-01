from django.urls import path
from . import views
from accounts.views import search_page, live_search

app_name = 'stores'

urlpatterns = [
    path('', views.home, name='home'),
    path('stores/', views.store_list, name='store_list'),
    path('stores/<str:slug>/', views.store_detail, name='store_detail'),
    
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/<int:product_id>/comment/', views.add_comment, name='add_comment'),

    path('category/<str:slug>/', views.category_products, name='category_products'),

    path('seller/stores/', views.manage_stores, name='manage_stores'),
    path('seller/stores/create/', views.create_store, name='create_store'),
    path('seller/stores/<int:pk>/edit/', views.edit_store, name='edit_store'),
    path('seller/stores/<int:pk>/delete/', views.delete_store, name='delete_store'),
    path('seller/stores/<int:store_id>/products/', views.manage_products, name='manage_products'),
    path('seller/products/<int:pk>/delete/', views.delete_product, name='delete_product'),
    path('seller/stores/<int:store_id>/withdraw/', views.withdraw_store_balance, name='withdraw_store_balance'),
    path('seller/products/<int:pk>/edit/', views.edit_product, name='edit_product'),


    path('cart/', views.cart_view, name='cart_view'),
    path('cart/add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('checkout/', views.checkout, name='checkout'),
    path('invoice/<int:order_id>/', views.invoice, name='invoice'),

    path('search/live/', live_search, name='live_search'),
    path('search/', search_page, name='search_page'),

    path('comment/<int:comment_id>/edit/', views.edit_comment, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', views.delete_comment, name='delete_comment'),
]
