from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib import messages
from .models import *
from .forms import StoreForm, ProductForm, CommentForm
from django.http import JsonResponse
from django.db.models import Q
from django.urls import reverse



def home(request):
    def get_products_by_parent(parent_slug):
        parent = Category.objects.filter(slug=parent_slug).first()
        if parent:
            cats = Category.objects.filter(Q(id=parent.id) | Q(parent=parent))
            return Product.objects.filter(category__in=cats).order_by("-created_at")
        return Product.objects.none()

    context = {
        'products': Product.objects.all().order_by("-created_at"),
        'latest_comments': Comment.objects.all().order_by("-created_at")[:5],
        
        'mobile_products': get_products_by_parent("موبایل"),
        'health_products': get_products_by_parent("سلامت-و-پزشکی"),
        'fashion_products': get_products_by_parent("مد-و-پوشاک"),
        'digital_products': get_products_by_parent("کالای-دیجیتال"),
        'home_products': get_products_by_parent("خانه-و-آشپزخانه"),
    }
    return render(request, 'stores/home.html', context)

def store_list(request):
    stores = Store.objects.all()
    return render(request, 'stores/store_list.html', {'stores': stores})

def store_detail(request, slug):
    store = get_object_or_404(Store, slug=slug)
    products = store.products.all()
    return render(request, 'stores/store_detail.html', {'store': store, 'products': products})

@login_required
def manage_stores(request):
    if not request.user.is_seller:
        raise PermissionDenied
    stores = Store.objects.filter(owner=request.user)
    return render(request, 'stores/seller/manage_stores.html', {'stores': stores})

@login_required
def create_store(request):
    if not request.user.is_seller:
        raise PermissionDenied
    if request.method == 'POST':
        form = StoreForm(request.POST)
        if form.is_valid():
            store = form.save(commit=False)
            store.owner = request.user
            store.save()
            return redirect('stores:manage_stores')
    else:
        form = StoreForm()
    return render(request, 'stores/seller/store_form.html', {'form': form})

@login_required
def edit_store(request, pk):
    store = get_object_or_404(Store, pk=pk, owner=request.user)
    if request.method == 'POST':
        form = StoreForm(request.POST, instance=store)
        if form.is_valid():
            form.save()
            return redirect('stores:manage_stores')
    else:
        form = StoreForm(instance=store)
    return render(request, 'stores/seller/store_form.html', {'form': form})

@login_required
def delete_store(request, pk):
    store = get_object_or_404(Store, pk=pk, owner=request.user)
    if request.method == 'POST':
        store.delete()
        return redirect('stores:manage_stores')
    return render(request, 'stores/seller/confirm_delete.html', {'obj': store})

@login_required
def manage_products(request, store_id):
    store = get_object_or_404(Store, pk=store_id, owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.store = store
            product.save()
            return redirect('stores:manage_products', store_id=store.id)
    else:
        form = ProductForm()
    products = store.products.all()
    return render(request, 'stores/seller/manage_products.html', {'store': store, 'products': products, 'form': form})

@login_required
def delete_product(request, pk):
    product = get_object_or_404(Product, pk=pk, store__owner=request.user)
    store_id = product.store.id
    if request.method == 'POST':
        product.delete()
        return redirect('stores:manage_products', store_id=store_id)
    return render(request, "accounts/delete_confirm.html", {
        "title": "حذف محصول",
        "message": f"آیا از حذف محصول «{product.name}» مطمئن هستید؟",
        "confirm_text": "بله، محصول را حذف کن",
        "cancel_url": reverse("stores:manage_products", args=[product.store.id]),
    })



@login_required
def add_to_cart(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if product.stock <= 0:
        return JsonResponse({'success': False, 'error': 'موجودی ناکافی'})
    
    cart_item, created = CartItem.objects.get_or_create(customer=request.user, product=product)
    
    if created:
        cart_item.quantity = 1
        cart_item.save()
    else:
        if cart_item.quantity < product.stock:
            cart_item.quantity += 1
            cart_item.save()
        else:
            return JsonResponse({'success': False, 'error': 'موجودی ناکافی'})
            
    total_items = sum(item.quantity for item in CartItem.objects.filter(customer=request.user))
    
    return JsonResponse({
        'success': True, 
        'quantity': cart_item.quantity, 
        'total_items': total_items,
        'item_id': cart_item.id 
    })


@login_required
def remove_from_cart(request, item_id):
    cart_item = get_object_or_404(CartItem, id=item_id, customer=request.user)
    delete_all = request.POST.get('delete_all') == '1'
    if delete_all:
        cart_item.delete()
        qty = 0
    else:
        if cart_item.quantity > 1:
            cart_item.quantity -= 1
            cart_item.save()
            qty = cart_item.quantity
        else:
            cart_item.delete()
            qty = 0
    total_items = sum(item.quantity for item in CartItem.objects.filter(customer=request.user))
    return JsonResponse({'success': True, 'quantity': qty, 'total_items': total_items})

@login_required
def cart_view(request):
    items = CartItem.objects.filter(customer=request.user)
    total = sum(item.product.final_price * item.quantity for item in items)
    return render(request, 'stores/cart.html', {'items': items, 'total': total})

@login_required
@transaction.atomic
def checkout(request):
    items = CartItem.objects.filter(customer=request.user).select_related('product', 'product__store')
    if not items.exists():
        return redirect('stores:home')
    total_amount = sum(item.product.final_price * item.quantity for item in items)
    if request.user.balance < total_amount:
        messages.error(request, 'موجودی کافی نیست.')
        return redirect('accounts:profile')
    request.user.balance -= total_amount
    request.user.save()
    order = Order.objects.create(customer=request.user, total_amount=total_amount)
    for item in items:
        if item.product.stock < item.quantity:
            messages.error(request, f'موجودی برای {item.product.name} کافی نیست.')
            transaction.set_rollback(True)
            return redirect('stores:cart_view')
        item.product.stock -= item.quantity
        item.product.save()
        item.product.store.balance += (item.product.final_price * item.quantity)
        item.product.store.save()
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.final_price
        )
    items.delete()
    messages.success(request, 'خرید موفقیت آمیز بود!')
    return redirect('stores:invoice', order_id=order.id)

@login_required
def invoice(request, order_id):
    order = get_object_or_404(Order, pk=order_id, customer=request.user)
    return render(request, 'stores/invoice.html', {'order': order})

@login_required
@transaction.atomic
def withdraw_store_balance(request, store_id):
    store = get_object_or_404(Store, pk=store_id, owner=request.user)
    if request.method == 'POST':
        amount_str = request.POST.get('amount')
        if amount_str and amount_str.isdigit():
            amount = int(amount_str)
            if 0 < amount <= store.balance:
                store.balance -= amount
                store.save()
                request.user.balance += amount
                request.user.save()
                messages.success(request, 'برداشت موفقیت آمیز بود.')
            else:
                messages.error(request, 'مبلغ نامعتبر.')
    return redirect('stores:manage_stores')

@login_required
def edit_product(request, pk):
    product = get_object_or_404(Product, pk=pk, store__owner=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            return redirect('stores:manage_products', store_id=product.store.id)
    else:
        form = ProductForm(instance=product)
    return render(request, 'stores/seller/edit_product.html', {'form': form, 'product': product})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    comments = product.comments.all().order_by('-created_at')
    comment_form = CommentForm()
    return render(request, 'stores/product_detail.html', {'product': product, 'comments': comments, 'comment_form': comment_form})

@login_required
def add_comment(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.product = product
            comment.user = request.user
            comment.save()
            messages.success(request, 'نظر شما با موفقیت ثبت شد.')
    return redirect('stores:product_detail', pk=product_id)

@login_required
def edit_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, user=request.user)
    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            messages.success(request, 'نظر شما با موفقیت ویرایش شد.')
            return redirect('stores:product_detail', pk=comment.product.id)
    else:
        form = CommentForm(instance=comment)
    return render(request, 'stores/edit_comment.html', {'form': form, 'comment': comment})

@login_required
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id)
    if comment.user == request.user or comment.product.store.owner == request.user:
        product_id = comment.product.id
        comment.delete()
        messages.success(request, 'نظر با موفقیت حذف شد.')
        return redirect('stores:product_detail', pk=product_id)
    else:
        raise PermissionDenied
    
def category_products(request, slug):
    category = get_object_or_404(Category, slug=slug)
    
    categories_to_filter = [category] + list(category.children.all())
    products = Product.objects.filter(category__in=categories_to_filter)
    
    return render(request, 'stores/category_products.html', {
        'category': category,
        'products': products
    })
