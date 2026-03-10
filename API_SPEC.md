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
    "name": "John Doe", "email": "john@example.com", "role": "user",
    "admin_id": "ADM-123" (required if role is admin)
  }
  ```
- **Response Data**: `{"access_token": "...", "message": "User registered successfully"}`

### `POST /auth/login`
- **Rate Limit**: 5 per minute
- **Payload**: `{"username": "jdoe", "password": "Password123!"}`
- **Response Data**: `{"access_token": "...", "message": "Login successful"}`

---

## Items Management

### `POST /items/lost`
- **Payload**: 
  ```json
  {
    "category": "Electronics", "item_type": "Phone", 
    "public_description": "Black iPhone 13", 
    "last_seen_location": "Library", "last_seen_datetime": "2024-03-20T10:00:00Z",
    "private_details": "Broken screen on top left"
  }
  ```
- **Response Data**: `{"item_id": 123, "message": "Lost item report created"}`

### `POST /items/found`
- **Payload**: 
  ```json
  {
    "category": "Electronics", "item_type": "Phone", 
    "public_description": "Black iPhone 13",
    "found_location": "Cafe", "found_datetime": "2024-03-20T11:00:00Z"
  }
  ```
- **Response Data**: `{"item_id": 124, "message": "Found item reported successfully"}`

### `GET /items/found`
- **Query Params**: `limit`, `offset`
- **Response Data**: 
  ```json
  {
    "items": [{"id": 124, "category": "...", ...}],
    "pagination": {"total": 1, "limit": 20, "offset": 0}
  }
  ```

### `GET /items/search`
- **Query Params**: `category`, `item_type`, `color`, `brand`, `query`, `limit`, `offset`
- **Response Data**: Similar to `/items/found` (paginated).

---

## Claims Management

### `POST /claims/submit`
- **Payload**: 
  ```json
  {
    "found_item_id": 124 (optional),
    "description": "I lost my phone at the cafe",
    "declared_value": 800.0,
    "receipt_proof": "http://img.url/receipt.jpg"
  }
  ```
- **Response Data**: `{"claim_id": 456, "message": "Claim submitted successfully"}`

### `GET /claims/pending`
- **Response Data**: List of claims associated with the user.

### `GET /claims/<int:claim_id>/potential-matches`
- **Description**: Returns list of found items that potentially match a specific claim.
- **Response Data**: `{"matches": [{"id": 124, "match_score": 95, ...}]}`

### `POST /claims/<int:claim_id>/link`
- **Payload**: `{"found_item_id": 124}`
- **Description**: Manually link a claim to a specific found item.

### `POST /claims/<int:claim_id>/schedule`
- **Payload**: `{"pickup_datetime": "2024-03-20T10:00:00", "pickup_location": "Main Office"}`
- **Description**: Schedule a pickup for an approved claim.

---

## Admin Operations

### `GET /admin/claims`
- **Description**: View all pending claims in the system.

### `POST /admin/claims/<id>/verify`
- **Role**: Admin only
- **Payload**: `{"decision": "approved" | "rejected" | "completed", "handover_notes": "..."}`
- **Response Data**: `{"message": "Claim verified successfully"}`

### `GET /admin/reports/transactions`
- **Description**: List all completed transactions.

### `GET /admin/reports/transactions/<int:claim_id>`
- **Description**: Detailed report for a specific completed transaction.

---

## Infrastructure

### `GET /status`
- **Description**: Verifies API and Database health.
- **Response**: 
  ```json
  {
    "status": "healthy",
    "services": {"api": "up", "database": "up"}
  }
  ```
