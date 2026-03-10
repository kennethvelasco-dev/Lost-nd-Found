# LostnFound API Specification

## Base URL
`http://localhost:5000/api`

## Authentication
All endpoints except `/auth/register` and `/auth/login` require a JWT in the `Authorization` header.

### `POST /auth/register`
- **Rate Limit**: 5 per minute
- **Payload**:
  ```json
  {
    "username": "jdoe",
    "password": "Password123!",
    "name": "John Doe",
    "email": "john@example.com",
    "role": "user"
  }
  ```

### `POST /auth/login`
- **Rate Limit**: 5 per minute
- **Payload**:
  ```json
  {
    "username": "jdoe",
    "password": "Password123!"
  }
  ```

---

## Items Management

### `GET /items/found`
- **Query Params**: `limit`, `offset`
- **Response**: Paginated list of found items with human-readable descriptions.

### `POST /items/found`
- **Payload**: Found item attributes (category, item_type, found_location, found_datetime, etc.)

### `GET /items/search`
- **Query Params**: `category`, `item_type`, `color`, `brand`, `query`, `limit`, `offset`
- **Response**: Paginated search results.

---

## Claims Management

### `POST /claims/submit`
- **Payload**: `found_item_id`, `description`, `declared_value`, `receipt_proof`

### `GET /claims/pending`
- **Response**: List of pending claims belonging to the user (or all if admin).

---

## Admin Operations

### `POST /admin/claims/<id>/verify`
- **Role**: Admin only
- **Payload**: `{"decision": "approved" | "rejected" | "completed", "handover_notes": "optional"}`

---

## Infrastructure

### `GET /status`
- **Response**: Health status of API and Database.
