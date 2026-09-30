from django.core.management.base import BaseCommand

from store.models import Category, Product

DATA = {
    "Electronics": [
        ("Wireless Headphones", "🎧", 2499, 25, "Over-ear Bluetooth headphones with 30-hour battery life and deep bass."),
        ("Smart Watch", "⌚", 3999, 15, "Track steps, heart rate and notifications with a bright AMOLED display."),
        ("Bluetooth Speaker", "🔊", 1799, 30, "Portable, waterproof speaker with 12 hours of playtime."),
        ("Mechanical Keyboard", "⌨️", 3299, 12, "Hot-swappable switches with RGB backlight and compact layout."),
    ],
    "Fashion": [
        ("Classic Backpack", "🎒", 1299, 40, "Water-resistant 25L backpack with padded laptop compartment."),
        ("Running Shoes", "👟", 2799, 20, "Lightweight, breathable shoes with responsive cushioning."),
        ("Sunglasses", "🕶️", 899, 50, "UV400 polarized lenses in a durable lightweight frame."),
        ("Denim Jacket", "🧥", 2199, 10, "Timeless regular-fit denim jacket, soft-washed cotton."),
    ],
    "Home": [
        ("Ceramic Coffee Mug", "☕", 349, 100, "350ml handmade-style mug, microwave and dishwasher safe."),
        ("Desk Lamp", "💡", 999, 35, "Adjustable LED lamp with three brightness modes and USB port."),
        ("Indoor Plant Pot", "🪴", 449, 60, "Minimal ceramic planter with drainage tray."),
        ("Scented Candle", "🕯️", 599, 0, "Soy wax candle with lavender and vanilla notes (currently sold out)."),
    ],
}


class Command(BaseCommand):
    help = "Load sample categories and products"

    def handle(self, *args, **opts):
        from django.utils.text import slugify
        for cat_name, products in DATA.items():
            cat, _ = Category.objects.get_or_create(name=cat_name, defaults={"slug": slugify(cat_name)})
            for name, emoji, price, stock, desc in products:
                Product.objects.update_or_create(
                    slug=slugify(name),
                    defaults=dict(category=cat, name=name, emoji=emoji, price=price, stock=stock, description=desc),
                )
        self.stdout.write(self.style.SUCCESS("Sample data loaded."))
