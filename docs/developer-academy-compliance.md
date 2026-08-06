# Developer Academy Compliance Matrix

Source checked: `docs/Checkliste Django_DRF-Projekte.pdf`.

Note: the request references `docs/developer-academy-checklist.pdf`, but the
available local checklist file is `docs/Checkliste Django_DRF-Projekte.pdf`.
This matrix uses the available PDF as the binding Developer Academy checklist.

| Requirement | Status | Evidence | Files | Action required |
| ----------- | ------ | -------- | ----- | --------------- |
| All endpoints are implemented according to documentation | Compliant | Endpoint paths, methods, serializers, permissions and tests were compared against `docs/requirements-matrix.md` and app URL files. | `core/urls.py`, `auth_app/api/urls.py`, `offers_app/api/urls.py`, `orders_app/api/urls.py`, `reviews_app/api/urls.py`, `docs/requirements-matrix.md` | Keep endpoint mapping below updated after changes. |
| Test coverage is at least 95 percent | Compliant | `coverage report --fail-under=95 -m` passed with 96 percent coverage. | `pyproject.toml`, `.github/workflows/backend-quality.yml`, app tests | None. |
| One function or method has one main responsibility | Compliant | Production logic is split by Models, Serializers, Views and Permissions; test setup helpers now express one setup task each. | app modules and app tests | Verified with tests and AST method scan. |
| Functions and methods have a maximum of 14 lines by default | Compliant | Final AST scan returned `no methods over 14 lines`. | all tracked Python files except migrations | Verified with AST scan command below. |
| No commented-out code or debug commands remain | Compliant | Debug scan found no application debug output, breakpoint calls, task markers or commented-out implementation. The only generated-output command is the documented README command for creating a local Django secret key. | Python files, `README.md`, `core/urls.py` | No action required. |
| Code is PEP8 compliant | Compliant | `black --check .`, `isort --check-only .` and `flake8 .` passed. | `pyproject.toml`, `setup.cfg`, Python files | None. |
| Code is documented/commented | Compliant | Concise English docstrings document env helpers, custom permissions, serializer validations, overridden create/update methods, dynamic querysets and aggregate/count views. | `core/settings.py`, `core/api_views.py`, app serializers, views, permissions, filters | None. |
| README is meaningful and explains how to start the project | Compliant | README contains project description, setup, env, migrations, superuser, server, tests, endpoints, roles and security notes. | `README.md` | None. |
| README is written in English | Compliant | README content is English. | `README.md` | None. |
| Backend is uploaded in its own repository without frontend | Compliant | Tracked files contain backend code only; frontend reference remains ignored. | `git ls-files`, `.gitignore`, `docs/frontend-reference/` | None. |
| Complete `requirements.txt` exists | Compliant | Runtime dependencies are listed; development tools are in `requirements-dev.txt`. | `requirements.txt`, `requirements-dev.txt` | None. |
| Database is never uploaded to GitHub | Compliant | `db.sqlite3` is ignored and not tracked. | `.gitignore`, `git status --ignored` | None. |
| Django project is named `core` | Compliant | Main Django package contains settings, urls, asgi and wsgi. | `core/settings.py`, `core/urls.py`, `core/asgi.py`, `core/wsgi.py` | None. |
| Apps have meaningful prefix or suffix | Compliant | Apps use clear names with `_app` suffix. | `auth_app`, `offers_app`, `orders_app`, `reviews_app` | None. |
| Each app with API functionality has an `api/` folder | Compliant | Each domain app has API serializers, views, urls and permissions where needed. | `auth_app/api/`, `offers_app/api/`, `orders_app/api/`, `reviews_app/api/` | None. |
| Admin environment is usable | Compliant | Relevant models are registered with list displays, filters and search fields; Django system check passes. | `auth_app/admin.py`, `offers_app/admin.py`, `orders_app/admin.py`, `reviews_app/admin.py` | None. |
| Model class names use PascalCase | Compliant | Own models use `User`, `Offer`, `OfferDetail`, `Order`, `Review`. | `auth_app/models.py`, `offers_app/models.py`, `orders_app/models.py`, `reviews_app/models.py` | None. |
| Model field names use snake_case | Compliant | Own model fields use snake_case names such as `created_at`, `delivery_time_in_days`, `business_user`. | app `models.py` files | None. |
| Models have meaningful `__str__()` and useful Meta options where needed | Compliant | Each domain model implements `__str__()` and Meta ordering/constraints are defined where useful. | app `models.py` files | None. |
| No request, API or permission logic in models | Compliant | Models contain data structure, constraints and display methods only. | app `models.py` files | None. |
| Model relationships use clear `related_name` and `on_delete` | Compliant | Foreign keys define `related_name` and `on_delete=models.CASCADE`. | `offers_app/models.py`, `orders_app/models.py`, `reviews_app/models.py` | None. |
| Use `ModelSerializer` for CRUD serializations | Compliant | CRUD serializers for User/Profile, Offer, OfferDetail, Order and Review use `ModelSerializer`; login uses plain `Serializer` because it does not map to a model CRUD resource. | app `api/serializers.py` files | None. |
| Serializer fields are explicit and never `__all__` | Compliant | Serializer fields are listed explicitly; `fields = "__all__"` search has no matches. | app `api/serializers.py` files | None. |
| Serializer fields are in expected order | Compliant | Fields follow documented request/response order from the requirements matrix. | `docs/requirements-matrix.md`, app serializers | None. |
| Serializer validation uses field validators and `validate()` appropriately | Compliant | Field checks use `validate_type`, `validate_features`, `validate_revisions`, `validate_status`, `validate_offer_detail_id`, `validate_business_user`, `validate_rating`; cross-field checks use `validate()`. | app serializers | None. |
| Use `ModelViewSet` for CRUD and APIView/GenericAPIView for custom endpoints | Compliant | CRUD resources use ViewSets; registration/login/list/count/base-info use DRF generic/API views. | app `api/views.py`, `core/api_views.py` | None. |
| `queryset` and `serializer_class` are class attributes | Compliant | View classes define serializers and static querysets where appropriate; dynamic access uses `get_queryset()`. | app `api/views.py` files | None. |
| Use `get_queryset()` for dynamic querysets | Compliant | User-specific and optimized querysets are implemented in `get_queryset()`. | `offers_app/api/views.py`, `orders_app/api/views.py`, `reviews_app/api/views.py`, `auth_app/api/views.py` | None. |
| Permissions are clearly declared with `permission_classes` | Compliant | Protected ViewSets and public auth endpoints declare explicit permissions. | app `api/views.py` files | None. |
| API routes are resource-oriented | Compliant | Routes use resource paths such as `/api/offers/`, `/api/orders/`, `/api/reviews/`, `/api/profile/<id>/`. | app URL files | None. |
| Each app has its own URL file | Compliant | Every domain app with API endpoints has `api/urls.py`. | app `api/urls.py` files | None. |
| Main project has central routing and includes all URLs | Compliant | `core/urls.py` includes all app URL modules and admin. | `core/urls.py` | None. |
| Each app has its own `permissions.py` where needed | Compliant | Apps with object or role access rules contain permissions modules. | app `api/permissions.py` files | None. |
| Permissions are logically combined | Compliant | Views combine `IsAuthenticated` with owner, participant, customer or business permissions. | app views and permissions | None. |
| No open endpoints without explicit reason | Compliant | Public endpoints are limited to registration, login and base-info; protected endpoints use authentication. | `auth_app/api/views.py`, `core/api_views.py`, app views | None. |
| Imports are grouped and sorted | Compliant | isort check passes and imports follow standard, third-party, local grouping. | Python files | None. |
| Responsibilities are separated between Models, Serializers, Views and Permissions | Compliant | Models store data, serializers validate/transform, views route API behavior, permissions enforce access. | app modules | None. |
| HTTP status codes are correct and tested | Compliant | Tests cover `201`, `204`, `400`, `403`, `404` and authentication failures; DRF defaults are used where possible. | app tests | None. |

## Endpoint Mapping

| Endpoint | URL | View | Serializer | Permission | Model | Tests |
| -------- | --- | ---- | ---------- | ---------- | ----- | ----- |
| Register user | `POST /api/registration/` | `RegistrationView` | `RegistrationSerializer` | `AllowAny` | `User` | `auth_app/tests/test_auth_api.py`, `auth_app/tests/test_security_regressions.py` |
| Login user | `POST /api/login/` | `LoginView` | `LoginSerializer` | `AllowAny` | `User`, `Token` | `auth_app/tests/test_auth_api.py`, `auth_app/tests/test_security_regressions.py` |
| Profile detail/update | `GET/PATCH /api/profile/<id>/` | `ProfileViewSet` | `ProfileSerializer` | `IsAuthenticated`, `IsProfileOwnerOrReadOnly` | `User` | `auth_app/tests/test_profile_api.py`, `auth_app/tests/test_security_regressions.py` |
| Business profiles | `GET /api/profiles/business/` | `BusinessProfileListView` | `ProfileSerializer` | default `IsAuthenticated` | `User` | `auth_app/tests/test_profile_api.py` |
| Customer profiles | `GET /api/profiles/customer/` | `CustomerProfileListView` | `ProfileSerializer` | default `IsAuthenticated` | `User` | `auth_app/tests/test_profile_api.py` |
| Offer list/create | `GET/POST /api/offers/` | `OfferViewSet` | `OfferSerializer` | `IsAuthenticated`, `IsBusinessOrReadOnly`, `IsOfferOwnerOrReadOnly` | `Offer`, `OfferDetail` | `offers_app/tests/test_offer_api.py` |
| Offer detail/update/delete | `GET/PATCH/DELETE /api/offers/<id>/` | `OfferViewSet` | `OfferSerializer` | `IsAuthenticated`, `IsBusinessOrReadOnly`, `IsOfferOwnerOrReadOnly` | `Offer`, `OfferDetail` | `offers_app/tests/test_offer_api.py` |
| Offer detail package | `GET /api/offerdetails/<id>/` | `OfferDetailViewSet` | `OfferDetailSerializer` | default `IsAuthenticated` | `OfferDetail` | `offers_app/tests/test_offer_api.py` |
| Order list/create | `GET/POST /api/orders/` | `OrderViewSet` | `OrderSerializer` | `IsAuthenticated`, `IsOrderParticipant`, `CanCreateOrUpdateOrder` | `Order`, `OfferDetail` | `orders_app/tests/test_order_api.py` |
| Order detail/update | `GET/PATCH /api/orders/<id>/` | `OrderViewSet` | `OrderSerializer` | `IsAuthenticated`, `IsOrderParticipant`, `CanCreateOrUpdateOrder` | `Order` | `orders_app/tests/test_order_api.py` |
| Open order count | `GET /api/order-count/<business_user_id>/` | `OrderCountView` | none | default `IsAuthenticated` | `Order`, `User` | `orders_app/tests/test_order_api.py` |
| Completed order count | `GET /api/completed-order-count/<business_user_id>/` | `CompletedOrderCountView` | none | default `IsAuthenticated` | `Order`, `User` | `orders_app/tests/test_order_api.py` |
| Review list/create | `GET/POST /api/reviews/` | `ReviewViewSet` | `ReviewSerializer` | `IsAuthenticated`, `IsCustomerOrReadOnly`, `IsReviewerOrReadOnly` | `Review` | `reviews_app/tests/test_review_api.py` |
| Review detail/update/delete | `GET/PATCH/DELETE /api/reviews/<id>/` | `ReviewViewSet` | `ReviewSerializer` | `IsAuthenticated`, `IsCustomerOrReadOnly`, `IsReviewerOrReadOnly` | `Review` | `reviews_app/tests/test_review_api.py` |
| Base info | `GET /api/base-info/` | `BaseInfoView` | none | `AllowAny` | `Review`, `Offer`, `User` | `core/tests/test_base_info_api.py` |

## Verification Commands

These commands were used for the final compliance review:

```bash
python manage.py check
python manage.py check --deploy
python manage.py makemigrations --check
python manage.py test --verbosity 2
coverage erase
coverage run manage.py test
coverage report --fail-under=95 -m
black --check .
isort --check-only .
flake8 .
debug-output grep scan
task-marker grep scan
explicit serializer field scan
git status
git diff
git diff main...HEAD
```

## Method-Length Result

Final AST scan result:

```text
no methods over 14 lines
```

No remaining method-length exception is required.
