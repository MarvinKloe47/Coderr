# Coderr Backend

Coderr is a Django and Django REST Framework backend for a service marketplace
where business users publish offers and customer users order packages and write
reviews.

## Implemented Scope

- Token authentication with registration and login endpoints
- Custom user model with `customer` and `business` roles
- Public profile data with owner-only profile updates
- Business offer CRUD with nested `basic`, `standard`, and `premium` packages
- Offer filtering, search, ordering, and paginated offer lists
- Customer order creation from offer details with immutable snapshots
- Business-only order status updates
- Customer reviews with duplicate and self-review protection
- Base statistics endpoint for the landing page
- Django admin registration for all domain models

## Technology Stack

- Python 3.14
- Django 6.0
- Django REST Framework
- DRF Token Authentication
- django-filter
- SQLite for local development
- Black, isort, flake8, Coverage

## Setup

```bash
git clone https://github.com/MarvinKloe47/Coderr.git
cd Coderr
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements-dev.txt
copy .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Generate a local secret key before editing `.env`:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

The API base URL is:

```text
http://127.0.0.1:8000/api/
```

Environment variables:

- `DJANGO_SECRET_KEY`: secret key for Django.
- `DJANGO_DEBUG`: `True` or `False`; use `True` only for local development.
- `DJANGO_ALLOWED_HOSTS`: comma-separated host names.
- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins without trailing slashes.

`.env.example` contains placeholders only. Do not use example values for
production.

This project uses SQLite for the Developer Academy submission and local
development. No external database, object storage, payment provider, or email
service is required by the implemented backend.

## Authentication

Use the returned token as:

```http
Authorization: Token <token>
```

Auth endpoints:

- `POST /api/registration/`
- `POST /api/login/`

Registration fields:

- `username`
- `email`
- `password`
- `repeated_password`
- `type`: `customer` or `business`

## Roles And Permissions

- Anonymous users can register, log in, and read `/api/base-info/`.
- Authenticated users can read profiles, offers, offer details, reviews, and
  their own related orders.
- Users can update only their own profile.
- Only business users can create offers.
- Only the offer owner can update or delete an offer.
- Only customer users can create orders.
- Orders are visible only to the customer and business user involved.
- Only the business user involved in an order can update its status.
- Only customer users can create reviews.
- Users cannot review themselves or review the same business twice.
- Only the reviewer can update or delete a review.

## Endpoint Groups

- Profiles: `/api/profile/<user_id>/`, `/api/profiles/business/`,
  `/api/profiles/customer/`
- Offers: `/api/offers/`, `/api/offers/<id>/`,
  `/api/offerdetails/<id>/`
- Orders: `/api/orders/`, `/api/orders/<id>/`,
  `/api/order-count/<business_user_id>/`,
  `/api/completed-order-count/<business_user_id>/`
- Reviews: `/api/reviews/`, `/api/reviews/<id>/`
- Statistics: `/api/base-info/`

## Filtering, Search, Ordering

Offer examples:

```http
GET /api/offers/?creator_id=2
GET /api/offers/?search=logo
GET /api/offers/?max_delivery_time=5
GET /api/offers/?ordering=min_price
GET /api/offers/?ordering=-updated_at&page=2
```

Review examples:

```http
GET /api/reviews/?business_user_id=2&ordering=-rating
GET /api/reviews/?reviewer_id=3&ordering=updated_at
```

## Tests And Quality

```bash
python manage.py check
python manage.py makemigrations --check
python manage.py test --verbosity 2
coverage erase
coverage run manage.py test
coverage report --fail-under=95 -m
black --check .
isort --check-only .
flake8 .
```

The project is configured to fail coverage reports below 95%.

## Project Structure

```text
core/
auth_app/
offers_app/
orders_app/
reviews_app/
```

Each domain app keeps API serializers, views, permissions, filters, and URLs in
its own `api/` package and tests in its own `tests/` package.

## Project Rules And Assumptions

- The implementation follows the provided Coderr frontend reference and the
  requirements matrix in `docs/requirements-matrix.md`.
- A user has exactly one role: `customer` or `business`.
- Registration and login return DRF tokens because the frontend authenticates
  with `Authorization: Token <token>`.
- Orders store a snapshot of the selected offer detail, so later changes to an
  offer do not rewrite existing orders.
- Offer lists are paginated with a page size of six to match the documented
  frontend expectations.
- Profile, offer, order, and review object access is enforced by DRF
  permissions and by querysets that limit visible records.

## Security

- Never commit `.env` files.
- Never store production secrets in source code.
- Generate a unique `DJANGO_SECRET_KEY` for every environment.
- Keep `DJANGO_DEBUG=False` outside local development.
- Configure allowed hosts and CORS origins explicitly.
- Use comma-separated CORS origins without trailing slashes.
- Rotate any credential that was accidentally committed.
- Do not use the example environment values in production.
- Do not add internal company domains, customer hosts, or production URLs as
  examples in documentation or tests.

If a secret is accidentally committed, remove it from the current code, rotate
or revoke it at the provider, and treat the historical value as compromised.
Do not rewrite public Git history or force-push without explicit approval.

Production HTTPS settings are controlled by environment variables:

- `DJANGO_SECURE_SSL_REDIRECT`
- `DJANGO_SECURE_HSTS_SECONDS`
- `DJANGO_SECURE_HSTS_INCLUDE_SUBDOMAINS`
- `DJANGO_SECURE_HSTS_PRELOAD`
- `DJANGO_SESSION_COOKIE_SECURE`
- `DJANGO_CSRF_COOKIE_SECURE`

## Troubleshooting

- If image uploads fail, ensure Pillow is installed from `requirements.txt`.
- If the frontend cannot reach the API, check `CORS_ALLOWED_ORIGINS`.
- If authentication fails, confirm the token header uses the `Token` prefix.
- If migrations are missing, run `python manage.py makemigrations --check`.

## Developer Academy Context

This repository contains the backend final project for the Developer Academy
Coderr assignment. The code is intentionally kept close to standard Django and
DRF patterns so the models, serializers, views, permissions, tests, and settings
can be explained during a project review.
