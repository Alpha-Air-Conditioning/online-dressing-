from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator
from .models import Product, Category, HeroBanner, Order, OrderItem, NewsletterSubscriber
import json
import random


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────
def get_cart(request):
    return request.session.get('cart', {})


def save_cart(request, cart):
    request.session['cart'] = cart
    request.session.modified = True


# ─────────────────────────────────────────────────────────────
# PAGES
# ─────────────────────────────────────────────────────────────
def homepage(request):
    latest_count = getattr(settings, 'LATEST_PRODUCTS_COUNT', 4)
    all_products = Product.objects.filter(stock__gt=0)
    latest_products = all_products[:latest_count]
    collection_products = all_products[latest_count:]
    hero_banners = HeroBanner.objects.filter(is_active=True)
    categories = Category.objects.all()
    return render(request, 'xeon/home.html', {
        'latest_products': latest_products,
        'collection_products': collection_products,
        'hero_banners': hero_banners,
        'categories': categories,
        'page_title': 'XEON | Luxury Fashion Store',
        'meta_description': 'Discover the latest fashion trends at XEON.',
    })


def collection(request):
    products = Product.objects.filter(stock__gt=0)
    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)
    search_query = request.GET.get('q', '')
    if search_query:
        products = products.filter(name__icontains=search_query)
    sort = request.GET.get('sort', '-created_at')
    sort_map = {'price_asc': 'price', 'price_desc': '-price', 'newest': '-created_at', 'oldest': 'created_at'}
    products = products.order_by(sort_map.get(sort, '-created_at'))
    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'xeon/collection.html', {
        'products': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
        'sort': sort,
        'page_title': 'Collection | XEON',
        'meta_description': 'Browse our full collection of premium fashion at XEON.',
        'total_count': paginator.count,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related_products = Product.objects.filter(category=product.category).exclude(id=product.id).filter(stock__gt=0)[:4]
    return render(request, 'xeon/product_detail.html', {
        'product': product,
        'related_products': related_products,
        'sizes': product.get_sizes_list(),
        'page_title': f'{product.name} | XEON',
        'meta_description': product.description[:160] if product.description else f'Buy {product.name} at XEON',
    })


def new_in(request):
    products = Product.objects.filter(is_new=True, stock__gt=0)
    paginator = Paginator(products, 12)
    return render(request, 'xeon/collection.html', {
        'products': paginator.get_page(request.GET.get('page')),
        'categories': Category.objects.all(),
        'page_title': 'New In | XEON',
        'section_title': 'NEW IN',
        'total_count': paginator.count,
    })


def archive_sale(request):
    # Only products that have a marked-down price
    products = Product.objects.filter(
        stock__gt=0,
        original_price__isnull=False
    ).exclude(original_price__lte=models.F('price'))

    categories = Category.objects.all()
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=selected_category)

    sort = request.GET.get('sort', 'newest')
    sort_map = {
        'price_asc':  'price',
        'price_desc': '-price',
        'newest':     '-created_at',
        'oldest':     'created_at',
        'discount':   'price',  # lowest price = biggest relative discount proxy
    }
    products = products.order_by(sort_map.get(sort, '-created_at'))

    paginator = Paginator(products, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(request, 'xeon/archive_sale.html', {
        'products': page_obj,
        'categories': categories,
        'selected_category': selected_category,
        'sort': sort,
        'total_count': paginator.count,
        'page_title': 'Archive Sale | XEON',
        'meta_description': 'Shop exclusive markdowns on past-season XEON favourites. Up to 50% off while stocks last.',
    })


# ─────────────────────────────────────────────────────────────
# AUTH VIEWS
# ─────────────────────────────────────────────────────────────
def login_view(request):
    if request.user.is_authenticated:
        return redirect('xeon:account')

    if request.method == 'POST':
        username_or_email = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        # allow login by email too
        user = authenticate(request, username=username_or_email, password=password)
        if user is None:
            # Try by email
            try:
                u = User.objects.get(email__iexact=username_or_email)
                user = authenticate(request, username=u.username, password=password)
            except User.DoesNotExist:
                pass

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.first_name or user.username}! 👋')
            next_url = request.GET.get('next', 'xeon:account')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid email/username or password. Please try again.')

    return render(request, 'xeon/auth/login.html', {
        'page_title': 'Login | XEON',
    })


def register_view(request):
    if request.user.is_authenticated:
        return redirect('xeon:account')

    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name  = request.POST.get('last_name', '').strip()
        email      = request.POST.get('email', '').strip()
        password1  = request.POST.get('password1', '')
        password2  = request.POST.get('password2', '')

        # Validations
        if not all([first_name, email, password1, password2]):
            messages.error(request, 'Please fill in all required fields.')
        elif password1 != password2:
            messages.error(request, 'Passwords do not match.')
        elif len(password1) < 8:
            messages.error(request, 'Password must be at least 8 characters.')
        elif User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'An account with this email already exists. Try logging in.')
        else:
            username = email.split('@')[0]
            base_username = username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f'{base_username}{counter}'
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                password=password1,
                first_name=first_name,
                last_name=last_name,
            )
            login(request, user)
            messages.success(request, f'Welcome to XEON, {first_name}! Your account has been created. 🎉')
            return redirect('xeon:account')

    return render(request, 'xeon/auth/register.html', {
        'page_title': 'Create Account | XEON',
    })


def logout_view(request):
    logout(request)
    messages.success(request, 'You have been logged out. See you soon!')
    return redirect('xeon:home')





@login_required(login_url='/login/')
def account_view(request):
    user = request.user
    orders = Order.objects.filter(email__iexact=user.email).order_by('-created_at')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_profile':
            user.first_name = request.POST.get('first_name', '').strip()
            user.last_name  = request.POST.get('last_name', '').strip()
            new_email = request.POST.get('email', '').strip()
            if new_email and new_email != user.email:
                if User.objects.filter(email__iexact=new_email).exclude(pk=user.pk).exists():
                    messages.error(request, 'That email is already in use.')
                else:
                    user.email = new_email
            user.save()
            messages.success(request, 'Profile updated successfully!')

        elif action == 'change_password':
            old_pass = request.POST.get('old_password', '')
            new_pass1 = request.POST.get('new_password1', '')
            new_pass2 = request.POST.get('new_password2', '')
            if not user.check_password(old_pass):
                messages.error(request, 'Current password is incorrect.')
            elif new_pass1 != new_pass2:
                messages.error(request, 'New passwords do not match.')
            elif len(new_pass1) < 8:
                messages.error(request, 'Password must be at least 8 characters.')
            else:
                user.set_password(new_pass1)
                user.save()
                update_session_auth_hash(request, user)
                messages.success(request, 'Password changed successfully!')

        return redirect('xeon:account')

    return render(request, 'xeon/auth/account.html', {
        'page_title': f'My Account | XEON',
        'orders': orders,
    })


# ─────────────────────────────────────────────────────────────
# CART
# ─────────────────────────────────────────────────────────────
def cart_view(request):
    cart = get_cart(request)
    cart_items = []
    subtotal = 0
    for key, item in cart.items():
        try:
            product = Product.objects.get(id=item['product_id'])
            line_total = product.price * item['quantity']
            subtotal += line_total
            cart_items.append({'key': key, 'product': product, 'size': item.get('size', ''), 'quantity': item['quantity'], 'line_total': line_total})
        except Product.DoesNotExist:
            pass
    shipping = 0 if subtotal >= 999 else 99
    return render(request, 'xeon/cart.html', {
        'cart_items': cart_items, 'subtotal': subtotal,
        'shipping': shipping, 'total': subtotal + shipping,
        'page_title': 'Your Cart | XEON',
    })


@require_POST
def add_to_cart(request):
    data = json.loads(request.body)
    product_id = str(data.get('product_id'))
    size = data.get('size', 'FREE')
    quantity = int(data.get('quantity', 1))
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'Product not found'}, status=404)
    cart = get_cart(request)
    cart_key = f"{product_id}_{size}"
    if cart_key in cart:
        cart[cart_key]['quantity'] += quantity
    else:
        cart[cart_key] = {'product_id': int(product_id), 'size': size, 'quantity': quantity}
    save_cart(request, cart)
    return JsonResponse({'success': True, 'message': f'{product.name} added to cart!', 'cart_count': sum(i['quantity'] for i in cart.values())})


@require_POST
def update_cart(request):
    data = json.loads(request.body)
    cart_key = data.get('key')
    quantity = int(data.get('quantity', 1))
    cart = get_cart(request)
    if cart_key in cart:
        if quantity <= 0:
            del cart[cart_key]
        else:
            cart[cart_key]['quantity'] = quantity
        save_cart(request, cart)
    return JsonResponse({'success': True, 'cart_count': sum(i['quantity'] for i in cart.values())})


@require_POST
def remove_from_cart(request):
    data = json.loads(request.body)
    cart_key = data.get('key')
    cart = get_cart(request)
    if cart_key in cart:
        del cart[cart_key]
        save_cart(request, cart)
    return JsonResponse({'success': True, 'cart_count': sum(i['quantity'] for i in cart.values())})


# ─────────────────────────────────────────────────────────────
# CHECKOUT
# ─────────────────────────────────────────────────────────────
def checkout(request):
    cart = get_cart(request)
    if not cart:
        messages.warning(request, 'Your cart is empty.')
        return redirect('xeon:cart')
    cart_items = []
    subtotal = 0
    for key, item in cart.items():
        try:
            product = Product.objects.get(id=item['product_id'])
            line_total = product.price * item['quantity']
            subtotal += line_total
            cart_items.append({'key': key, 'product': product, 'size': item.get('size', ''), 'quantity': item['quantity'], 'line_total': line_total})
        except Product.DoesNotExist:
            pass
    shipping = 0 if subtotal >= 999 else 99
    total = subtotal + shipping

    if request.method == 'POST':
        order = Order.objects.create(
            session_key=request.session.session_key or '',
            full_name=request.POST.get('full_name', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            address=request.POST.get('address', ''),
            city=request.POST.get('city', ''),
            pincode=request.POST.get('pincode', ''),
            total_amount=total,
        )
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item['product'], size=item['size'], quantity=item['quantity'], price=item['product'].price)
        save_cart(request, {})
        messages.success(request, f'Order #{order.id} placed successfully!')
        return redirect('xeon:order_success', order_id=order.id)

    # Pre-fill if logged in
    prefill = {}
    if request.user.is_authenticated:
        prefill = {'full_name': request.user.get_full_name(), 'email': request.user.email}

    return render(request, 'xeon/checkout.html', {
        'cart_items': cart_items, 'subtotal': subtotal, 'shipping': shipping, 'total': total,
        'prefill': prefill, 'page_title': 'Checkout | XEON',
    })


def order_success(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    return render(request, 'xeon/order_success.html', {'order': order, 'page_title': 'Order Confirmed | XEON'})


# ─────────────────────────────────────────────────────────────
# NEWSLETTER
# ─────────────────────────────────────────────────────────────
@require_POST
def newsletter_subscribe(request):
    data = json.loads(request.body)
    email = data.get('email', '').strip()
    if email:
        _, created = NewsletterSubscriber.objects.get_or_create(email=email)
        if created:
            return JsonResponse({'success': True, 'message': 'Thank you for subscribing!'})
        return JsonResponse({'success': False, 'message': 'You are already subscribed.'})
    return JsonResponse({'success': False, 'message': 'Please enter a valid email.'})


def about(request):
    return render(request, 'xeon/about.html', {'page_title': 'About Us | XEON'})


def contact(request):
    return render(request, 'xeon/contact.html', {'page_title': 'Contact Us | XEON'})
