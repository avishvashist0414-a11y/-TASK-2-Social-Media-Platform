from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .cart import Cart
from .forms import CheckoutForm, RegisterForm
from .models import Category, Order, OrderItem, Product


def product_list(request):
    products = Product.objects.select_related("category")
    categories = Category.objects.all()
    current = request.GET.get("category")
    q = request.GET.get("q", "").strip()
    if current:
        products = products.filter(category__slug=current)
    if q:
        products = products.filter(Q(name__icontains=q) | Q(description__icontains=q))
    return render(request, "store/product_list.html",
                  {"products": products, "categories": categories, "current": current, "q": q})


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    related = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]
    return render(request, "store/product_detail.html", {"product": product, "related": related})


def cart_detail(request):
    cart = Cart(request)
    return render(request, "store/cart.html", {"items": list(cart), "total": cart.total})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        qty = max(1, int(request.POST.get("quantity", 1)))
    except ValueError:
        qty = 1
    cart = Cart(request)
    if product.stock == 0:
        msg, ok = f"{product.name} is out of stock.", False
    else:
        cart.add(product, qty)
        msg, ok = f"Added {product.name} to your cart.", True
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({"ok": ok, "message": msg, "count": len(cart)}, status=200 if ok else 400)
    (messages.success if ok else messages.error)(request, msg)
    return redirect(request.POST.get("next") or "cart_detail")


@require_POST
def cart_update(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    try:
        qty = int(request.POST.get("quantity", 1))
    except ValueError:
        qty = 1
    Cart(request).set(product, qty)
    return redirect("cart_detail")


@require_POST
def cart_remove(request, product_id):
    Cart(request).remove(get_object_or_404(Product, pk=product_id))
    return redirect("cart_detail")


@login_required
def checkout(request):
    cart = Cart(request)
    items = list(cart)
    if not items:
        messages.info(request, "Your cart is empty.")
        return redirect("product_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    order = form.save(commit=False)
                    order.user = request.user
                    order.total = cart.total
                    order.save()
                    for it in items:
                        # lock the row so concurrent orders can't oversell
                        product = Product.objects.select_for_update().get(pk=it["product"].pk)
                        if product.stock < it["quantity"]:
                            raise ValueError(f"Not enough stock for {product.name}.")
                        product.stock -= it["quantity"]
                        product.save(update_fields=["stock"])
                        OrderItem.objects.create(order=order, product=product, name=product.name,
                                                 price=product.price, quantity=it["quantity"])
            except ValueError as e:
                messages.error(request, str(e))
                return redirect("cart_detail")
            cart.clear()
            return redirect("order_success", order_id=order.id)
    else:
        form = CheckoutForm(initial={"email": request.user.email,
                                     "full_name": request.user.get_full_name()})
    return render(request, "store/checkout.html", {"form": form, "items": items, "total": cart.total})


@login_required
def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id, user=request.user)
    return render(request, "store/order_success.html", {"order": order})


@login_required
def order_list(request):
    orders = request.user.orders.prefetch_related("items")
    return render(request, "store/order_list.html", {"orders": orders})


def register(request):
    if request.user.is_authenticated:
        return redirect("product_list")
    form = RegisterForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Welcome! Your account has been created.")
        return redirect("product_list")
    return render(request, "registration/register.html", {"form": form})
