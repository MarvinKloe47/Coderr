# Coderr Backend

Coderr is a Django and Django REST Framework backend for a service marketplace
where business users publish offers and customer users order packages and write
reviews.

## Features

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

The API base URL is:

```text
http://127.0.0.1:8000/api/
```

Environment variables:

- `DJANGO_SECRET_KEY`: secret key for Django.
- `DJANGO_DEBUG`: `True` or `False`.
- `DJANGO_ALLOWED_HOSTS`: comma-separated host names.
- `CORS_ALLOWED_ORIGINS`: comma-separated frontend origins.

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
coverage report -m
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

## Security Notes

- Do not commit `.env`, `db.sqlite3`, media files, coverage output, or virtual
  environments.
- Set a strong `DJANGO_SECRET_KEY` outside development.
- Set `DJANGO_DEBUG=False` outside local development.
- Restrict `DJANGO_ALLOWED_HOSTS` and `CORS_ALLOWED_ORIGINS` for deployment.

## Troubleshooting

- If image uploads fail, ensure Pillow is installed from `requirements.txt`.
- If the frontend cannot reach the API, check `CORS_ALLOWED_ORIGINS`.
- If authentication fails, confirm the token header uses the `Token` prefix.
- If migrations are missing, run `python manage.py makemigrations --check`.

## Developer Academy Context

This backend was implemented from scratch for the Developer Academy Coderr
backend final project. The API behavior follows the provided frontend reference
and the requirements matrix in `docs/requirements-matrix.md`.
