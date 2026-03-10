# LostnFound API Specification

## Base URL
`http://localhost:5000/api`

## Response Envelope
All responses follow this standard envelope:
```json
{
  "success": true,
  "message": "Information message",
  "data": { ... }
}
```

## Authentication

### `POST /auth/register`
- **Rate Limit**: 5 per minute
- **Payload**:
  ```json
  {
    "username": "jdoe", "password": "Password123!",
    "name": "John Doe", "email": "john@example.com", "role": "user"
  }
  ```
- **Response Data**: `{"access_token": "...", "message": "..."}`

### `POST /auth/login`
- **Rate Limit**: 5 per minute
- **Payload**: `{"username": "jdoe", "password": "Password123!"}`
- **Response Data**: `{"access_token": "...", "message": "..."}`

---

## Items Management

### `POST /items/found`
- **Payload**: Found item attributes (category, item_type, found_location, found_datetime, etc.)
- **Response Data**: `{"item_id": 123, "message": "..."}`

### `GET /items/found`
- **Query Params**: `limit`, `offset`
- **Response Data**: 
  ```json
  {
    "items": [...],
    "pagination": {"total": 100, "limit": 20, "offset": 0}
  }
  ```

### `GET /items/search`
- **Query Params**: `category`, `item_type`, `color`, `brand`, `query`, `limit`, `offset`
- **Response Data**: Similar to `/items/found` (paginated).

---

## Claims Management

### `POST /claims/submit`
- **Payload**: `found_item_id`, `description`, `declared_value`, `receipt_proof` (optional extra fields allowed)
- **Response Data**: `{"claim_id": 456, "score": 85, "message": "..."}`

### `GET /claims/pending`
- **Response Data**: List of pending claims with found item details.

---

## Admin Operations

### `POST /admin/claims/<id>/verify`
- **Role**: Admin only
- **Payload**: `{"decision": "approved" | "rejected" | "completed", "handover_notes": "optional"}`
- **Response Data**: `{"message": "Claim approved successfully"}`

---

## Infrastructure

### `GET /status`
- **Response**: `{"status": "healthy", "database": "connected"}`
