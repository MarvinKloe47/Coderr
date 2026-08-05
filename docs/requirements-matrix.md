# Coderr API Requirements Matrix

## Source Review

Reviewed before the first backend code change:

- `docs/project-rules.md`: empty.
- `docs/implementation-notes.md`: empty.
- `docs/api-examples/README.md`: empty.
- `docs/frontend-reference/README.md`: frontend usage notes only.
- `docs/frontend-reference/project.Coderr-main/project.Coderr-main/README.md`: frontend project overview.
- `docs/Checkliste Django_DRF-Projekte.pdf`: general Django/DRF Definition of Done, naming conventions, API structure, permissions, status-code guidance, README and coverage requirements.
- Unpacked frontend reference code under `docs/frontend-reference/project.Coderr-main/project.Coderr-main/`, especially `shared/scripts/config.js`, `api.js`, `auth.js`, `user_crud.js`, `offer_crud.js`, `order_crud.js`, `review_crud.js`, `scripts/profile.js`, `scripts/business_profile.js`, `scripts/customer_profile.js`, and the template files.

No OpenAPI/Swagger/Postman file with canonical Coderr responses is present in `docs/`. The frontend reference is therefore the only endpoint-specific material. Assumptions below are marked explicitly.

## Global API Conventions

- Base URL expected by the frontend: `http://127.0.0.1:8000/api/`.
- Authentication header: `Authorization: Token <token>`.
- Authenticated endpoints should return `401 Unauthorized` for missing/invalid token unless object-level permission rules produce `403 Forbidden`.
- JSON endpoints use `Content-Type: application/json`.
- Profile and offer image updates use `multipart/form-data`.
- Offer lists are paginated. Frontend page size constant: `6`.
- Offer list response must be DRF pagination-compatible: `count`, `next`, `previous`, `results`.
- Stable ordering is required for paginated responses.

## Endpoint Matrix

| Endpoint | Methods | Auth | Roles | Request Fields | Response Fields Used By Frontend | Query Parameters | Expected Status Codes | Permission Rules | Frontend Calls |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| `/api/registration/` | `POST` | Public | anonymous | `username`, `email`, `password`, `repeated_password`, `type` (`business` or `customer`) | `token`, `user_id`, `username` | none | `201`, `400` | Reject duplicate usernames/emails, invalid role, password mismatch. Create user and matching profile. | `auth.js`, `registration.js`, `registration.html` |
| `/api/login/` | `POST` | Public | anonymous | `username`, `password` | `token`, `user_id`, `username` | none | `200`, `400` or `401` | Only valid credentials receive a token. | `auth.js`, `login.html` |
| `/api/profile/<user_id>/` | `GET`, `PATCH` | Required | customer, business | `PATCH` multipart fields: `first_name`, `last_name`, `email`, optional `file`; business also `tel`, `location`, `description`, `working_hours` | `user`, `username`, `first_name`, `last_name`, `email`, `file`, `location`, `tel`, `description`, `working_hours`, `type`, `created_at` | none | `200`, `400`, `401`, `403`, `404` | Any authenticated user can read a profile. Only the profile owner can update it. Role-specific fields should only be writable where relevant. | `user_crud.js`, `profile.js`, `business_profile.js`, `customer_profile.js`, `single_offer.js` |
| `/api/profiles/business/` | `GET` | Required | customer, business | none | list items with `user`, `username`, `first_name`, `last_name`, `file`, `location`, `tel`, `description`, `working_hours`, `type`; nested `user` objects are tolerated by frontend transformer | none | `200`, `401` | Authenticated users can list public business profiles. | `user_crud.js` |
| `/api/profiles/customer/` | `GET` | Required | customer, business | none | list items with `user`, `username`, `first_name`, `last_name`, `file`, `type`; nested `user` objects are tolerated by frontend transformer | none | `200`, `401` | Authenticated users can list public customer profiles. | `user_crud.js` |
| `/api/offers/` | `GET`, `POST` | `GET` required by frontend flow; `POST` required | business for `POST` | `POST` JSON: `title`, `description`, `details` array with exactly `basic`, `standard`, `premium`; each detail has `title`, `revisions`, `delivery_time_in_days`, `price`, `features` | list: `id`, `user`, `title`, `description`, `image`, `created_at`, `updated_at`, `details`, `min_price`, `min_delivery_time`; create returns at least `id` | `creator_id`, `search`, `ordering`, `page`, `max_delivery_time` | `200`, `201`, `400`, `401`, `403` | Only business users create offers. Customer users cannot create offers. | `offer_crud.js`, `offer_list.js`, `profile.js`, `business_profile.js` |
| `/api/offers/<id>/` | `GET`, `PATCH`, `DELETE` | Required | owner business for write/delete | `PATCH` JSON: same editable fields as create; `PATCH` multipart with `image` for upload | detail/list-compatible fields: `id`, `user`, `title`, `description`, `image`, `created_at`, `updated_at`, `details`, `min_price`, `min_delivery_time` | none | `200`, `204`, `400`, `401`, `403`, `404` | Any authenticated user can read. Only offer owner can update or delete. | `offer_crud.js`, `single_offer.js` |
| `/api/offerdetails/<id>/` | `GET` | Required | customer, business | none | `id`, `offer`, `title`, `revisions`, `delivery_time_in_days`, `price`, `features`, `offer_type` | none | `200`, `401`, `404` | Authenticated users can read offer details. | `offer_crud.js`, `single_offer.js` |
| `/api/orders/` | `GET`, `POST` | Required | customer, business for `GET`; customer for `POST` | `POST` JSON: `offer_detail_id` | list/create: `id`, `customer_user`, `business_user`, `created_at`, `status`, `title`, `delivery_time_in_days`, `revisions`, `price`, `features` | none | `200`, `201`, `400`, `401`, `403`, `404` | Users see only orders where they are customer or business party. Only customers create orders. Order data must snapshot selected offer detail. | `order_crud.js`, `profile.js` |
| `/api/orders/<id>/` | `PATCH` | Required | participating business user | `status` (`in_progress`, `completed`, `cancelled`) | updated order fields, especially `status` | none | `200`, `400`, `401`, `403`, `404` | Status updates are used from the business profile UI. Assumption: only the order's business user may update status; customers have read-only access. | `order_crud.js`, `profile.js` |
| `/api/reviews/` | `GET`, `POST` | Required | customer, business for `GET`; customer for `POST` | `POST` JSON: `business_user`, `description`, `rating` | `id`, `business_user`, `reviewer`, `description`, `rating`, `created_at`, `updated_at` | `business_user_id`, `reviewer_id`, `ordering` | `200`, `201`, `400`, `401`, `403` | No self-review. One review per reviewer/business user pair. Assumption: only customer users create reviews, because frontend exposes review creation through customer behavior. | `review_crud.js`, `business_profile.js`, `customer_profile.js`, `single_offer.js` |
| `/api/reviews/<id>/` | `PATCH`, `DELETE` | Required | review owner | `PATCH` JSON: `description`, `rating` | updated review fields | none | `200`, `204`, `400`, `401`, `403`, `404` | Only the reviewer can edit or delete their review. | `review_crud.js` |
| `/api/base-info/` | `GET` | Public or required not stated | anonymous, customer, business | none | Assumption from landing page: aggregate counts for `review_count`, `average_rating`, `business_profile_count`, `offer_count` or close frontend-facing names. | none | `200` | Read-only aggregate endpoint. | `index.js` |
| `/api/order-count/<business_user_id>/` | `GET` | Required | customer, business | none | `order_count` | none | `200`, `401`, `404` | Counts in-progress orders for a business user. | `offer_crud.js`, `single_offer.js` |
| `/api/completed-order-count/<business_user_id>/` | `GET` | Required | customer, business | none | `order_count` | none | `200`, `401`, `404` | Counts completed orders for a business user. | `offer_crud.js`, `business_profile.js` |

## Offer Filtering, Search, Ordering

- `creator_id`: filters offers by owner user id.
- `search`: frontend search box forwards free text; assumption: search over offer `title` and `description`.
- `max_delivery_time`: filters offers whose minimum or detail delivery time is at most the given day count. Assumption: use the minimum detail delivery time for list-level filtering because the list displays `min_delivery_time`.
- `ordering`: frontend passes values such as `updated_at`, `-updated_at`, and may use price/delivery ordering from UI controls. Assumption: support `updated_at`, `min_price`, and `min_delivery_time`, including descending variants.
- `page`: standard DRF page number.

## Review Filtering, Search, Ordering

- `business_user_id`: reviews received by a business user.
- `reviewer_id`: reviews written by a customer/user.
- `ordering`: frontend uses `-updated_at`, `updated_at`, `-rating`, `rating`.

## Data Model Requirements Derived From Frontend

- Users need a stable numeric id used as `user` in profile responses and as `auth-user-id` in local storage.
- User roles: `customer`, `business`.
- Profiles store shared fields: `user`, `username`, `first_name`, `last_name`, `email`, `file`, `type`, `created_at`.
- Business profiles additionally store/display: `location`, `tel`, `description`, `working_hours`.
- Offers belong to a business user and include exactly three detail variants: `basic`, `standard`, `premium`.
- Offer details include `features` as an ordered list of strings.
- `revisions = -1` represents unlimited revisions.
- Orders snapshot offer detail fields: `title`, `delivery_time_in_days`, `revisions`, `price`, `features`.
- Orders use status values `in_progress`, `completed`, `cancelled`.
- Reviews belong to a reviewer and a business user and use a 1-5 star `rating`.

## Open Or Contradictory Requirements

- The official endpoint documentation mentioned in the task is not present as OpenAPI, Swagger, Postman, or populated Markdown.
- Public versus authenticated read access for offers and `base-info` is not explicit. The frontend's pages usually set authentication before deeper interactions, but the landing page calls `base-info` without checking auth.
- Exact error response text is not documented. Use DRF-standard field errors with clear German/English-neutral messages where custom validation is needed.
- Exact profile list response shape allows either flat `user` id or nested user object; `transformApiResponse()` supports both. Prefer flat documented fields for consistency.
- Exact ordering options in offer UI are partly inferred from state and templates. Implement the observed values and document any additional standard DRF ordering fields in README.
- Draft PR creation and workflow-status verification depend on GitHub authentication being available in the environment.
