from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Category, Order, Product


class StoreFlowTests(TestCase):
    def setUp(self):
        cat = Category.objects.create(name="Test", slug="test")
        self.p = Product.objects.create(category=cat, name="Widget", slug="widget",
                                        description="d", price=100, stock=5)

    def test_pages_load(self):
        self.assertEqual(self.client.get(reverse("product_list")).status_code, 200)
        self.assertEqual(self.client.get(self.p.get_absolute_url()).status_code, 200)

    def test_cart_add_ajax_and_stock_cap(self):
        r = self.client.post(reverse("cart_add", args=[self.p.id]), {"quantity": 99},
                             headers={"x-requested-with": "XMLHttpRequest"})
        self.assertEqual(r.json()["count"], 5)  # capped at stock

    def test_checkout_requires_login(self):
        self.client.post(reverse("cart_add", args=[self.p.id]), {"quantity": 1})
        r = self.client.get(reverse("checkout"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/login/", r.url)

    def test_register_and_full_order(self):
        r = self.client.post(reverse("register"), {"username": "anu", "email": "a@b.com",
                             "password1": "S3cure-pass!x", "password2": "S3cure-pass!x"})
        self.assertEqual(r.status_code, 302)
        self.client.post(reverse("cart_add", args=[self.p.id]), {"quantity": 2})
        r = self.client.post(reverse("checkout"), {"full_name": "Anu", "email": "a@b.com",
                             "address": "1 Road", "city": "Agra", "postal_code": "282001"})
        order = Order.objects.get()
        self.assertRedirects(r, reverse("order_success", args=[order.id]))
        self.assertEqual(order.total, 200)
        self.assertEqual(order.items.count(), 1)
        self.p.refresh_from_db()
        self.assertEqual(self.p.stock, 3)

    def test_login_logout(self):
        User.objects.create_user("bob", password="pw12345!x")
        self.assertTrue(self.client.login(username="bob", password="pw12345!x"))
        self.assertEqual(self.client.get(reverse("order_list")).status_code, 200)
