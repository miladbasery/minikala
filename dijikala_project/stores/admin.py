from django.contrib import admin
from .models import Category, Store, Product, Comment, CartItem, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'parent')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'slug')
    list_filter = ('parent',)


@admin.register(Store)
class StoreAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'balance', 'slug')
    list_filter = ('owner',)
    search_fields = ('name', 'owner__phone_number', 'slug')
    prepopulated_fields = {'slug': ('name',)}


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 0
    fields = ('user', 'rating', 'text', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'store',
        'category',
        'price',
        'discount_percent',
        'final_price_display',
        'stock',
        'created_at',
    )
    list_filter = ('category', 'store', 'created_at')
    search_fields = ('name', 'description')
    list_editable = ('price', 'discount_percent', 'stock')
    readonly_fields = ('created_at',)
    inlines = [CommentInline]

    @admin.display(description='قیمت نهایی')
    def final_price_display(self, obj):
        return obj.final_price


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('product__name', 'user__phone_number', 'text')
    readonly_fields = ('created_at',)


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ('customer', 'product', 'quantity')
    search_fields = ('customer__phone_number', 'product__name')
    list_filter = ('customer',)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'total_amount', 'date')
    list_filter = ('date',)
    search_fields = ('customer__phone_number',)
    inlines = [OrderItemInline]
    readonly_fields = ('total_amount', 'date')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'product', 'quantity', 'price')
    search_fields = ('order__id', 'product__name')
    list_filter = ('order',)
