from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import login
from .models import Product, Inquiry, SampleRequest, Order, Cart, CartItem, OrderItem
from .forms import BuyerRegistrationForm

def about(request):
    return render(request, 'core/about.html')

def product_list(request):
    category = request.GET.get('category')
    products = Product.objects.filter(is_active=True)
    categories = Product.objects.values_list('category', flat=True).distinct()

    if category:
        products = products.filter(category=category)

    return render(request, 'core/product_list.html', {
        'products': products,
        'categories': categories
    })

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk)
    return render(request, 'core/product_detail.html', {'product': product})

@login_required
def send_inquiry(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        quantity = request.POST.get('quantity')
        target_price = request.POST.get('target_price')
        message_text = request.POST.get('message')

        Inquiry.objects.create(
            buyer=request.user,
            product=product,
            requested_quantity=quantity,
            target_price=target_price,
            message=message_text
        )
        messages.success(request, 'Inquiry sent successfully!')
        return redirect('product_detail', pk=pk)
    return redirect('product_detail', pk=pk)

@login_required
def request_sample(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        # Check if already requested recently
        existing = SampleRequest.objects.filter(buyer=request.user, product=product, status='Pending').exists()
        if existing:
            messages.warning(request, 'You already have a pending sample request for this product.')
        else:
            SampleRequest.objects.create(buyer=request.user, product=product)
            messages.success(request, 'Sample requested successfully!')
    return redirect('product_detail', pk=pk)

@login_required
def dashboard(request):
    inquiries = Inquiry.objects.filter(buyer=request.user).order_by('-created_at')
    orders = Order.objects.filter(buyer=request.user).order_by('-created_at')
    samples = SampleRequest.objects.filter(buyer=request.user).order_by('-created_at')

    return render(request, 'core/dashboard.html', {
        'inquiries': inquiries,
        'orders': orders,
        'samples': samples
    })

def register(request):
    if request.method == 'POST':
        form = BuyerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful! Welcome.')
            return redirect('product_list')
    else:
        form = BuyerRegistrationForm()
    return render(request, 'core/register.html', {'form': form})

def contact(request):
    return render(request, 'core/contact.html')

@login_required
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        # Ensure quantity is at least the MOQ or 1
        if quantity < 1:
            quantity = 1
            
        cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
        
        if not item_created:
            cart_item.quantity += quantity
        else:
            cart_item.quantity = quantity
        cart_item.save()
        
        messages.success(request, f'Added {product.style_name} to your cart.')
        return redirect(request.META.get('HTTP_REFERER', 'product_list'))
    
    # Fallback if GET (quick add)
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, product=product)
    if not item_created:
        cart_item.quantity += 1
    cart_item.save()
    messages.success(request, f'Added {product.style_name} to your cart.')
    return redirect(request.META.get('HTTP_REFERER', 'product_list'))

@login_required
def view_cart(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'core/cart.html', {'cart': cart})

@login_required
def update_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity > 0:
            cart_item.quantity = quantity
            cart_item.save()
            messages.success(request, 'Cart updated.')
        else:
            cart_item.delete()
            messages.warning(request, 'Item removed from cart.')
    return redirect('view_cart')

@login_required
def remove_from_cart(request, pk):
    cart_item = get_object_or_404(CartItem, pk=pk, cart__user=request.user)
    cart_item.delete()
    messages.success(request, 'Item removed from cart.')
    return redirect('view_cart')

@login_required
def checkout(request):
    cart, created = Cart.objects.get_or_create(user=request.user)
    if not cart.items.exists():
        messages.warning(request, 'Your cart is empty.')
        return redirect('product_list')
        
    if request.method == 'POST':
        import uuid
        from django.utils import timezone
        
        # Create single order for the cart
        order_number = f"ORD-{str(uuid.uuid4())[:8].upper()}"
        
        order = Order.objects.create(
            order_number=order_number,
            buyer=request.user,
            delivery_date=timezone.now().date() + timezone.timedelta(days=30), # Default 30 days
            status='Confirmed'
        )
        
        for item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                unit_price=item.product.target_price
            )
            
        # Clear cart
        cart.items.all().delete()
        messages.success(request, f'Order #{order_number} placed successfully!')
        return redirect('dashboard')
        
    return render(request, 'core/checkout.html', {'cart': cart})
