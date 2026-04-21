# LostnFound API Specification

## Base URL

- Local development: `http://localhost:5000/api`
- Production (Render): `https://lost-nd-found.onrender.com/api`

The frontend (Vercel) calls the backend at:

- `BASE_URL/auth/...`
- `BASE_URL/items/...`
- `BASE_URL/claims/...`
- `BASE_URL/admin/...`

---

## Response Format

- **Description**: Most routes return JSON in one of these forms:

```json
{
  "success": true,
  "message": "Information message",
  "data": { ... }
}
```

## Authentication

### `POST /auth/register`

- **Rate Limit**: 3 per 15 minutes
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
- **Response Data**:
  ```json
  {
    "success": true,
    "message": "User registered successfully."
  }
  ```
- **Note**: In this deployment, accounts are automatically verified upon registration for ease of use. A mock verification email is logged to the server console.

### `POST /auth/login`

- **Rate Limit**: 10 per 15 minutes
- **Payload**:
  ```json
  { "username": "jdoe", "password": "Password123!" }
  ```
- **Response Data**:
  ```json
  {
    "success": true,
    "message": "Login successful",
    "data": {
      "access_token": "<JWT>",
      "user": {
        "id": 1,
        "username": "jdoe",
        "role": "user",
        "name": "John Doe"
      }
    }
  }
  ```

---

## Items Management

### `POST /items/lost`

- **Payload**:
  ```json
  {
    "category": "Electronics",
    "item_type": "Phone",
    "color": "Black",
    "last_seen_location": "Library",
    "last_seen_datetime": "2024-03-20T10:00:00Z",
    "public_description": "Black iPhone 13",
    "private_details": "Broken screen on top left",
    "main_picture": "data:image/jpeg;base64,...",
    "additional_picture_1": "data:image/jpeg;base64,...",
    "additional_picture_2": "data:image/jpeg;base64,..."
  }
  ```
- **Response Data**:
  ```json
  {
    "success": true,
    "message": "Lost item created successfully",
    "data": { "item_id": 123 }
  }
  ```

### `GET /items/lost`

- **Query Params**:
  - status – usually "lost"
  - query – free-text search (description/category/type)
  - sort – e.g. "item_type", "found_datetime", "created_at", "found_location"
- **Response Data**:
  ```json
  {
  "success": true,
  "data": {
    "items": [ { "id": 124, "category": "Electronics", "item_type": "Phone", ... } ],
    "pagination": { "total": 1, "limit": 20, "offset": 0 }
  }
  }
  ```

### `GET /items/released`

- **Description**: Fetch all items that have been successfully returned/released.
- **Query Params**:
  - query – search by claimant name, category, or item type
  - limit, offset – for pagination
- **Response Data**:
  ```json
  {
    "success": true,
    "data": {
      "items": [
        {
          "id": 1,
          "original_report_id": "UUID",
          "item_source": "found",
          "category": "Electronics",
          "item_type": "Phone",
          "color": "Black",
          "brand": "Apple",
          "claimant_name": "John Smith",
          "released_by_admin": "admin_user",
          "main_picture": "data:image/jpeg;base64,...",
          "last_seen_location": "Science Library",
          "found_location": null,
          "resolved_at": "..."
        }
      ],
      "pagination": { "total": 1, "limit": 20, "offset": 0 }
    }
  }
  ```

### `GET /items/returned` (Legacy Alias)

- **Description**: Alias for `/items/released` for backward compatibility.

### `GET /items/my-activities`

- **Description**: Return the current user’s combined reports and claims (used by MyActivities.jsx).
- **Response Data**:
  ```json
  {
    "success": true,
    "data": {
      "reports": [
        /* lost_items + found_items owned by user */
      ],
      "claims": [
        /* claims owned by user */
      ]
    }
  }
  ```

### `GET /items/pending`

- **Description**: Admin: list pending reports for approval (used by AdminReports.jsx).

### `POST /items/reports/:id/verify`

- **Description**: Admin: approve or reject a specific report.
- **Payload**:
  ```json
  {
    "type": "lost" | "found",
    "decision": "approved" | "rejected",
    "reason": "optional rejection reason"
  }
  ```

### `POST /items/reports/:type/:id/dismiss`

- **Description**: User: dismiss a resolved report from “My Activities”.

### `POST /items/claims/:id/dismiss`

- **Description**: User: dismiss a resolved claim from “My Activities”.

### `POST /items/found` (optional / if enabled)

- **Description**: Create a found item report.
- **Payload**:
  ```json
  {
    "category": "Electronics",
    "item_type": "Phone",
    "public_description": "Black iPhone 13",
    "found_location": "Cafe",
    "found_datetime": "2024-03-20T11:00:00Z"
  }
  ```

### `GET /items/search` (optional / if enabled)

- **Description**: Full-text and structured search over items.
- **Query Params**: category, item_type, color, brand, query, limit, offset
- **Response Data**: Similar to /items/lost (paginated).

### `GET /items/found`

- **Query Params**: `limit`, `offset`
- **Response Data**:
  ```json
  {
    "items": [{"id": 124, "category": "...", ...}],
    "pagination": {"total": 1, "limit": 20, "offset": 0}
  }
  ```

---

## Claims Management

### `POST /claims/submit`

- **Payload**:
  ```json
  {
    "found_item_id": 124,
    "claimant_name": "Jane Doe",
    "claimant_email": "jane@example.com",
    "description": "I lost my phone at the cafe",
    "declared_value": 800,
    "receipt_proof": "data:image/jpeg;base64,...",
    "answers": {
      "claimed_category": "Electronics",
      "claimed_item_type": "Phone",
      "claimed_brand": "Apple",
      "claimed_color": "Black",
      "lost_location_claimed": "Campus Cafe",
      "lost_datetime_claimed": "2024-03-20T10:00:00Z"
    }
  }
  ```
- **Response Data**:
  ```json
  {
    "success": true,
    "message": "Claim submitted successfully",
    "data": {
      "claim_id": 456,
      "score": 72
    }
  }
  ```

### `GET /claims/pending`

- **Description**: List claims filtered by decision (used by AdminClaimList.jsx and AdminApprovedClaims.jsx).
- **Query Param s**: status – "pending", "approved", "rejected", "completed"
- **Response Data**:
  ```json
  {
  "success": true,
  "data": [ { "id": 456, "user_name": "jdoe", "item_type": "Phone", "score": 72, ... } ]
  }
  ```

### `GET /claims/<int:claim_id>`

- **Description**: Get detailed information for a claim (used by AdminClaimDetail.jsx).

### `POST /claims/<int:claim_id>/verify`

- **Description**: Admin: approve or reject a claim.
- **Payload**:
  ```json
  { "decision": "approved" | "rejected" }
  ```

### `POST /claims/<int:claim_id>/schedule`

- **Description**: Schedule a pickup for an approved claim.
- **Payload**:
  ```json
  {
    "pickup_datetime": "2024-03-20T10:00:00",
    "pickup_location": "Main Office"
  }
  ```

### `GET /claims/<int:claim_id>/potential-matches`

- **Description**: Returns a list of items that potentially match a specific claim.

### `POST /claims/<int:claim_id>/link`

- **Description**: Manually link a claim to a specific found or lost item.

---

## Admin Operations

### `GET /admin/stats`

- **Description**: Return high-level dashboard statistics (used by `AdminDashboard.jsx`).

- **Response Data**:

  ```json
  {
    "success": true,
    "data": {
      "total_lost": 12,
      "total_found": 8,
      "pending_claims": 3,
      "resolved_items": 5
    }
  }
  ```

- **Note**: Claim and report moderation flows use /claims/_ and /items/_ as described above, not /admin/claims.

### `POST /claims/<id>/verify`

- **Role**: Admin only
- **Payload**: `{"decision": "approved" | "rejected" | "completed", "handover_notes": "..."}`
- **Response Data**: `{"success": true, "data": { ... }}`

### `GET /items/released` (Formerly Transaction Reports)

- **Description**: Access completed "transactions" via the released items endpoint.

---

## Infrastructure

### `GET /api/status`

- **Description**: Verifies API and Database health.
- **Response**:
  ```json
  {
    "status": "healthy",
    "services": { "api": "up", "database": "up" }
  }
  ```
- **Status**: 200 OK if both API and DB are reachable.
