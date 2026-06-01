
# MiniKala (مینی‌کالا) — Open Source Multi‑Vendor Marketplace (Django)

MiniKala is an open-source, Persian (fa-IR), RTL-first multi-vendor marketplace built with Django.  
It provides a clean foundation for building a Digikala-like experience: product catalog, categories, stores (vendors), cart, checkout, orders/invoices, comments, user profiles, and seller management.

| Image 1 | Image 2 | Image 3 | Image 4 | Image 5 |

| :---: | :---: | :---: | :---: | :---: |

| ![Description 1](https://i.postimg.cc/43P10RXc/image-2026-05-24-04-11-27.png) | ![Description 2](https://i.postimg.cc/YSzXwmz7/image-2026-05-24-04-10-26.png) | ![Description 3](https://i.postimg.cc/YSzXwmz7/image-2026-05-24-04-10-26.png) | ![Description 4](https://i.postimg.cc/MKJdXD3W/image-2026-05-24-04-13-54.png) | ![Description 5](https://i.postimg.cc/SKPG47z4/image-2026-05-24-04-15-53.png) |

---

## What this project does

MiniKala is designed as a practical marketplace MVP with two primary roles:

### Buyer / Customer
- Sign up / log in
- Browse products and categories
- Search products, stores, and categories
- Add/remove items to cart
- Checkout using wallet balance (internal balance)
- View orders and invoice
- Comment on products, edit/delete own comments
- Manage profile and increase wallet balance

### Seller / Vendor
- Seller signup flow
- Create and manage stores
- Add/edit/delete products (with stock management)
- Receive revenue into store balance on each successful checkout
- Withdraw store balance into personal wallet balance

### Platform / System
- Category hierarchy (parent/child)
- Global navbar category listing
- Live search (AJAX) suggestions for products/categories/stores
- RTL UI and Persian localization settings
- Basic error pages (400/403/404/500)
- Theme switching (dark/light) persisted in localStorage

---

## Who this is for

This repository is useful for:
- Developers building a Persian RTL marketplace MVP
- Teams wanting a multi-vendor architecture starter (stores + products + checkout)
- Students learning Django by reading a real-world structure (apps, views, templates, context processors)
- Anyone who wants a clean base to extend with payments, shipping, admin customizations, REST APIs, etc.

---

## Tech stack

- Python
- Django 6.x
- SQLite (default) or PostgreSQL (optional)
- HTML templates + static CSS/JS (RTL-first)
- Pillow for image handling

---

## Requirements (Python packages)

The project uses these pinned dependencies:

- asgiref==3.11.1  
- Django==6.0.5  
- django-jazzmin==3.0.4 (optional; currently commented in settings)  
- pillow==12.2.0  
- psycopg2==2.9.12  
- psycopg2-binary==2.9.12  
- sqlparse==0.5.5  
- tzdata==2026.2  

---

## Installation

### 1) Clone the repository
```bash
git clone https://github.com/miladbasery/<REPO_NAME>.git
cd <REPO_NAME>
```

### 2) Create and activate a virtual environment

Linux/macOS:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3) Install dependencies
```bash
pip install -r requirements.txt
```

### 4) Apply migrations
```bash
python manage.py migrate
```

### 5) Create an admin user (optional but recommended)
```bash
python manage.py createsuperuser
```

### 6) Run the development server
```bash
python manage.py runserver
```

Open:
- http://127.0.0.1:8000

---

## Static & media configuration

The project uses:
- `STATIC_URL = '/static/'`
- `STATICFILES_DIRS = [BASE_DIR / 'static']`
- `STATIC_ROOT = BASE_DIR / 'staticfiles'`
- `MEDIA_URL = '/media/'`
- `MEDIA_ROOT = BASE_DIR / 'media'`

For development, ensure you serve media in `urls.py` (recommended setup):

```python
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # ...
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Database

### Default: SQLite (no extra setup)
By default the project uses SQLite:

```python
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.sqlite3",
    "NAME": BASE_DIR / "db.sqlite3",
  }
}
```

This is ideal for local development and quick demos.

---

## Sharing a database with others (recommended options)

You said you want to share the database as well. Here are the senior-friendly approaches:

### Option A (best for demo/testing): Share a sanitized SQLite snapshot
1. Run migrations and populate sample data (or your demo data).
2. Stop the server.
3. Share the `db.sqlite3` file.

Notes:
- Do **not** share real user data or credentials.
- Consider creating a dedicated demo admin user.
- If you include `db.sqlite3` in the repo, add a clear warning and keep it sanitized.

### Option B (best for teams): Use PostgreSQL and share connection settings
For a collaborative environment, PostgreSQL is the right choice.

1) Install PostgreSQL and create a database/user:
```sql
CREATE DATABASE minikala;
CREATE USER minikala_user WITH PASSWORD 'strong_password';
GRANT ALL PRIVILEGES ON DATABASE minikala TO minikala_user;
```

2) Update `settings.py`:
```python
DATABASES = {
  "default": {
    "ENGINE": "django.db.backends.postgresql",
    "NAME": "dijikala",
    "USER": "dijikala_user",
    "PASSWORD": "strong_password",
    "HOST": "127.0.0.1",
    "PORT": "5432",
  }
}
```

3) Install driver (already present in requirements):
- psycopg2 / psycopg2-binary

4) Run:
```bash
python manage.py migrate
```

### Important security note
Never commit real production database credentials into Git.  
Use environment variables (`.env`) and keep secrets out of the repository.

---

## Project structure (high-level)

- `accounts/`  
  Authentication, signup flows (customer/seller), profile, wallet balance, public profile.

- `stores/`  
  Categories, stores (vendors), products, cart, checkout, orders/invoice, comments, seller management pages.

- `templates/`  
  Server-rendered HTML templates, including a shared `base.html` with RTL layout, navigation, category menus, and live search UI.

- `static/`  
  CSS, JS, images/logos.

- `media/`  
  Uploaded files (product images, profile images, etc.).

---

## Key features implemented (behavioral summary)

- **Cart logic** is per authenticated user via `CartItem`.
- **Stock protection** prevents adding beyond available inventory.
- **Checkout** is transactional (`@transaction.atomic`):
  - Deducts customer wallet balance
  - Creates an Order + OrderItems
  - Decreases product stock
  - Increases store balance
  - Clears cart
- **Live Search** endpoint returns JSON lists of products/stores/categories.
- **Seller restrictions** are enforced via `PermissionDenied` where needed.

---

## License

This project is open source.  
If you want it to be clearly reusable, add a `LICENSE` file (MIT/Apache-2.0/GPL-3.0 are common).  
Recommendation for maximum adoption: MIT.

---

## Credits

Built by **Milad**, with love.  
LinkedIn: https://www.linkedin.com/in/miladbasery  
GitHub: https://github.com/miladbasery
