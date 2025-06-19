# 🗃️ Schema: `public`

## `tenants`

| Field         | Type     | Description                             |
| ------------- | -------- | --------------------------------------- |
| id            | UUID PK  | Tenant ID                               |
| name          | string   | Agency name                             |
| schema_name   | string   | PostgreSQL schema name (e.g. `agency1`) |
| custom_domain | string   | `agency-1.com`                          |
| plan_id       | UUID FK  | Refers to `plans.id`                    |
| created_at    | datetime |                                         |

## `plans`

| Field           | Type    | Description |
| --------------- | ------- | ----------- |
| id              | UUID PK | Plan ID     |
| name            | string  | Plan name   |
| max_users       | int     |             |
| max_properties  | int     |             |
| price_per_month | decimal |             |

## `domain_verification`

| Field              | Type    | Description                  |
| ------------------ | ------- | ---------------------------- |
| id                 | UUID PK |                              |
| tenant_id          | UUID FK | Refers to `tenants.id`       |
| domain             | string  | Custom domain to verify      |
| status             | enum    | `pending`, `verified`        |
| verification_token | string  | For DNS or file verification |

## `public.users`

| Field         | Type     | Description             |
| ------------- | -------- | ----------------------- |
| id            | UUID PK  |                         |
| email         | string   |                         |
| password_hash | string   | Hashed password         |
| role          | enum     | `superadmin`, `support` |
| created_at    | datetime |                         |

## `stripe_accounts`

| Field             | Type     | Description            |
| ----------------- | -------- | ---------------------- |
| id                | UUID PK  |                        |
| tenant_id         | UUID FK  | Refers to `tenants.id` |
| stripe_account_id | string   | Stripe Connect Account |
| mode              | enum     | `live` or `test`       |
| created_at        | datetime |                        |

## `subscriptions`

| Field                  | Type     | Description                 |
| ---------------------- | -------- | --------------------------- |
| id                     | UUID PK  |                             |
| tenant_id              | UUID FK  | Refers to `tenants.id`      |
| stripe_subscription_id | string   | Stripe Billing ID           |
| status                 | enum     | `active`, `cancelled`, etc. |
| current_period_end     | datetime |                             |

# 🏢 Schema: `tenant` (per agency)

## `users`

| Field         | Type     | Description                   |
| ------------- | -------- | ----------------------------- |
| id            | UUID PK  |                               |
| email         | string   |                               |
| password_hash | string   |                               |
| full_name     | string   |                               |
| role          | enum     | `admin`, `employee`, `client` |
| created_at    | datetime |                               |

## `clients`

| Field     | Type    | Description         |
| --------- | ------- | ------------------- |
| id        | UUID PK |                     |
| full_name | string  |                     |
| email     | string  |                     |
| phone     | string  |                     |
| user_id   | UUID FK | Links to `users.id` |

## `properties`

| Field       | Type     | Description                   |
| ----------- | -------- | ----------------------------- |
| id          | UUID PK  |                               |
| title       | string   |                               |
| description | text     |                               |
| price       | decimal  |                               |
| status      | enum     | `available`, `rented`, `sold` |
| address     | JSON     | street, city, zip, etc.       |
| listed_at   | datetime |                               |
| agent_id    | UUID FK  | FK to `users.id`              |

## `property_images`

| Field       | Type    | Description             |
| ----------- | ------- | ----------------------- |
| id          | UUID PK |                         |
| property_id | UUID FK | FK to `properties.id`   |
| image_url   | string  |                         |
| is_cover    | bool    | Is this the main image? |

## `appointments`

| Field         | Type     | Description                         |
| ------------- | -------- | ----------------------------------- |
| id            | UUID PK  |                                     |
| visitor_name  | string   |                                     |
| visitor_email | string   |                                     |
| property_id   | UUID FK  | FK to `properties.id`               |
| scheduled_at  | datetime |                                     |
| status        | enum     | `pending`, `confirmed`, `cancelled` |
| agent_id      | UUID FK  | FK to `users.id`                    |

## `contracts`

| Field                | Type     | Description                 |
| -------------------- | -------- | --------------------------- |
| id                   | UUID PK  |                             |
| property_id          | UUID FK  |                             |
| buyer_name           | string   |                             |
| status               | enum     | `draft`, `sent`, `signed`   |
| docusign_envelope_id | string   | External envelope reference |
| created_at           | datetime |                             |

## `client_properties`

| Field                 | Type    | Description                    |
| --------------------- | ------- | ------------------------------ |
| id                    | UUID PK |                                |
| client_id             | UUID FK | FK to `clients.id`             |
| property_id           | UUID FK | FK to `properties.id`          |
| ownership_percentage  | decimal | For shared investment tracking |
| amount_invested       | decimal | Optional                       |
| monthly_rent_expected | decimal | Optional                       |

## `payouts`

| Field       | Type     | Description           |
| ----------- | -------- | --------------------- |
| id          | UUID PK  |                       |
| client_id   | UUID FK  | FK to `clients.id`    |
| amount      | decimal  |                       |
| paid_at     | datetime |                       |
| property_id | UUID FK  | FK to `properties.id` |

## `settings`

| Field           | Type    | Description           |
| --------------- | ------- | --------------------- |
| id              | UUID PK |                       |
| logo_url        | string  |                       |
| primary_color   | string  | CSS color hex         |
| secondary_color | string  |                       |
| timezone        | string  | e.g., `Europe/Madrid` |
