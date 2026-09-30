from decimal import Decimal

from .models import Product


class Cart:
    """Session-based shopping cart: {product_id: quantity}."""

    KEY = "cart"

    def __init__(self, request):
        self.session = request.session
        self.data = self.session.setdefault(self.KEY, {})

    def _save(self):
        self.session.modified = True

    def add(self, product, quantity=1):
        pid = str(product.id)
        new_qty = min(self.data.get(pid, 0) + quantity, product.stock)
        if new_qty > 0:
            self.data[pid] = new_qty
        self._save()

    def set(self, product, quantity):
        pid = str(product.id)
        if quantity <= 0:
            self.data.pop(pid, None)
        else:
            self.data[pid] = min(quantity, product.stock)
        self._save()

    def remove(self, product):
        self.data.pop(str(product.id), None)
        self._save()

    def clear(self):
        self.session[self.KEY] = {}
        self._save()

    def __len__(self):
        return sum(self.data.values())

    def __iter__(self):
        products = Product.objects.in_bulk([int(i) for i in self.data])
        for pid, qty in self.data.items():
            product = products.get(int(pid))
            if product:
                yield {"product": product, "quantity": qty, "subtotal": product.price * qty}

    @property
    def total(self):
        return sum((i["subtotal"] for i in self), Decimal("0.00"))
