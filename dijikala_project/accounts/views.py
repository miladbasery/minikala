from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from .forms import CustomerSignupForm, SellerSignupForm, ProfileUpdateForm, AddBalanceForm
from stores.models import Order, Category, Product, Store, Comment
from .models import User
from django.urls import reverse


def login_view(request):
    if request.method == 'POST':
        u = request.POST.get('username')
        p = request.POST.get('password')
        user = authenticate(request, username=u, password=p)
        if user is not None:
            login(request, user)
            return redirect('stores:home')
        messages.error(request, 'شماره موبایل یا رمز عبور اشتباه است.')
    return render(request, 'accounts/login.html')

def signup_customer(request):
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('stores:home')
    else:
        form = CustomerSignupForm()
    return render(request, 'accounts/signup.html', {'form': form, 'type': 'خریدار'})

def signup_seller(request):
    if request.method == 'POST':
        form = SellerSignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('stores:home')
    else:
        form = SellerSignupForm()
    return render(request, 'accounts/signup.html', {'form': form, 'type': 'فروشنده'})

@login_required
def profile_view(request):
    orders = Order.objects.filter(customer=request.user).order_by('-date')[:5]
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            p_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user)
            if p_form.is_valid():
                p_form.save()
                messages.success(request, 'پروفایل بروزرسانی شد.')
                return redirect('accounts:profile')
        elif 'add_balance' in request.POST:
            b_form = AddBalanceForm(request.POST)
            if b_form.is_valid():
                request.user.balance += b_form.cleaned_data['amount']
                request.user.save()
                messages.success(request, 'موجودی افزایش یافت.')
                return redirect('accounts:profile')
    else:
        p_form = ProfileUpdateForm(instance=request.user)
        b_form = AddBalanceForm()
    return render(request, 'accounts/profile.html', {'p_form': p_form, 'b_form': b_form, 'orders': orders})

@login_required
def delete_account(request):
    if request.method == 'POST':
        user = request.user
        logout(request)
        user.delete()
        return redirect('stores:home')
    return render(request, "accounts/delete_confirm.html", {
        "title": "حذف دائمی حساب",
        "message": "آیا از حذف دائمی حساب کاربری خود اطمینان دارید؟\nبا این کار تمامی اطلاعات شما غیرقابل بازگشت خواهد بود.",
        "confirm_text": "بله، حسابم را حذف کن",
        "cancel_url": reverse("accounts:profile"),
    })

def public_profile(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    orders = Order.objects.filter(customer=target_user)
    comments = Comment.objects.filter(user=target_user).select_related('product')
    return render(request, 'accounts/public_profile.html', {
        'target_user': target_user,
        'total_purchases': orders.count(),
        'total_spent': sum(o.total_amount for o in orders),
        'comments': comments
    })

def live_search(request):
    q = request.GET.get('q', '').strip()
    if not q: return JsonResponse({'products': [], 'stores': [], 'categories': []})
    return JsonResponse({
        'products': [{'id': p.id, 'name': p.name} for p in Product.objects.filter(name__icontains=q)[:3]],
        'stores': [{'id': s.id, 'name': s.name} for s in Store.objects.filter(name__icontains=q)[:3]],
        'categories': [{'id': c.id, 'name': c.name} for c in Category.objects.filter(name__icontains=q)[:3]]
    })

def search_page(request):
    q = request.GET.get('q', '').strip()
    return render(request, 'search.html', {
        'query': q,
        'products': Product.objects.filter(name__icontains=q) if q else [],
        'stores': Store.objects.filter(name__icontains=q) if q else []
    })

def about_us(request): return render(request, 'accounts/about.html')
def terms(request): return render(request, 'accounts/terms.html')
def error_400(request, exception): return render(request, 'errors/400.html', status=400)
def error_403(request, exception): return render(request, 'errors/403.html', status=403)
def error_404(request, exception): return render(request, 'errors/404.html', status=404)
def error_500(request): return render(request, 'errors/500.html', status=500)
