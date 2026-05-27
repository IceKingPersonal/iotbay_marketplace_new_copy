# Orders API (Feature 03)

Base URL: `http://localhost:5000/api`  
Auth: Flask **session cookie** (log in via `POST /api/auth/login` first).  
Frontend uses `apiRequest()` with `credentials: "include"`.

## Roles

| Role | Create order | List | View detail | Update / cancel |
|------|--------------|------|-------------|-----------------|
| **customer** | Yes | Own orders only | Own orders | Saved orders only → Paid or Cancelled |
| **staff** | No | All customer orders | All customer orders | No (read-only) |

## Status rules

- New orders are created with status **`Saved`**.
- Stock is **decremented** when the order is created.
- Customers may update **only `Saved`** orders (before paid).
- **`Saved` → `Paid`** or **`Saved` → `Cancelled`**.
- On **`Cancelled`**, stock is **restored**; the order row stays in the database.

## Endpoints

### `POST /api/orders` (customer only)

Create an order from one or more device lines.

**Body:**

```json
{
  "shipping_address": "1 Test Street, Sydney",
  "currency": "AUD",
  "items": [
    { "product_id": 1, "quantity": 2 },
    { "product_id": 2, "quantity": 1 }
  ]
}
```

**Rules:**

- `items` must be non-empty.
- Each product must have **stock_qty ≥ 1** and enough stock for the requested quantity.
- `total_price` is calculated server-side (sum of quantity × unit price at order time).

**Response `201`:**

```json
{
  "order": { "order_id": 1, "status": "Saved", "total_price": 9097, ... },
  "items": [ ... ]
}
```

### `GET /api/orders`

**Customer:** own orders.  
**Staff:** all orders placed by users with `role = 'customer'`.

**Query (optional, mainly for customers):**

| Param | Example | Description |
|-------|---------|-------------|
| `order_id` | `5` | Exact order ID |
| `date` | `2026-05-27` | Prefix match on `created_at` |

### `GET /api/orders/:orderId`

Order header + line items (with device names when `products` row exists).

### `PATCH /api/orders/:orderId` (customer only)

Partial update — **status only**.

```json
{ "status": "Paid" }
```

or

```json
{ "status": "Cancelled" }
```

Only allowed when current status is **`Saved`**.

### `PUT /api/orders/:orderId` (customer only)

Full update of a **Saved** order: shipping address, currency, and **replace all line items**.

Same body shape as `POST` (`shipping_address`, `currency`, `items`). Stock is adjusted (old lines restored, new lines deducted).

## Integration for Cart / Checkout (Feature 07)

When checkout completes, call:

```http
POST /api/orders
Cookie: <session>
Content-Type: application/json
```

with cart lines mapped to `{ product_id, quantity }`.

## Database tables (orders feature)

- `products` — `product_id`, `price` (cents), `stock_qty`, …
- `orders` — `order_id`, `user_id`, `status`, `total_price`, …
- `order_items` — `order_id`, `product_id`, `quantity`, `unit_price`

Run `python init_db.py` in `backend/` to create tables and sample products.

## Sample users

| Email | Password | Role |
|-------|----------|------|
| customer@test.com | Password123 | customer |
| staff@test.com | Password123 | staff |
