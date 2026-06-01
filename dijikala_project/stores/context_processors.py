from .models import Category , CartItem

def global_template_data(request):
    return {
        'categories': Category.objects.filter(parent__isnull=True).prefetch_related('children')
    }

def cart_data(request):
    cart_quantities = {}
    cart_total_items = 0

    if request.user.is_authenticated:
        items = CartItem.objects.filter(customer=request.user)
        for item in items:
            cart_quantities[item.product.id] = item.quantity
            cart_total_items += item.quantity

    return {
        'cart_quantities': cart_quantities,
        'cart_total_items': cart_total_items,
    }
