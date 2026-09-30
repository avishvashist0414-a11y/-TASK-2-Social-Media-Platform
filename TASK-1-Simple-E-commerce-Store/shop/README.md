# 🛒 ShopEasy — Simple E-commerce Store

A basic e-commerce website built with **Django (Python)** + HTML/CSS/JavaScript and an **SQLite** database.

## Features
- Product listing with category filter and search
- Product details page (with related products)
- Shopping cart (session based; add without reload via JavaScript, update qty, remove)
- User registration / login / logout
- Checkout & order processing (stock is checked and decremented atomically)
- Order history for each user
- Django admin to manage products, categories and orders
- Database models: `Category`, `Product`, `Order`, `OrderItem` + Django `User`

## Tech stack
| Layer | Tech |
|---|---|
| Frontend | HTML (Django templates), CSS, vanilla JavaScript |
| Backend | Django 5+ |
| Database | SQLite (swap in PostgreSQL/MySQL in `config/settings.py`) |

## Run locally
```bash
git clone https://github.com/AnuragSharma338/TASK-1-Simple-E-commerce-Store.git
cd TASK-1-Simple-E-commerce-Store

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt

python manage.py migrate
python manage.py seed           # load sample products
python manage.py createsuperuser  # optional, for /admin
python manage.py runserver
```
Open http://127.0.0.1:8000/

## Run tests
```bash
python manage.py test
```

## Project structure
```
config/            project settings & root urls
store/
  models.py        Category, Product, Order, OrderItem
  cart.py          session cart
  views.py         listing, detail, cart, checkout, orders, register
  templates/       HTML pages
  static/store/    css + js
  management/commands/seed.py   sample data
```

## Notes
- Payment is simulated (no real gateway) — this is a demo.
- Before deploying set `DEBUG = False`, a real `SECRET_KEY`, and `ALLOWED_HOSTS`.
