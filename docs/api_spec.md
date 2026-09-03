# API Specification

## Base URL

```
Development: http://localhost:8000/api
Production: https://api.krishix.com/api
```

## Authentication

All authenticated endpoints require a Bearer token in the Authorization header:

```
Authorization: Bearer <access_token>
```

Tokens are obtained via login and expire after 30 minutes.

---

## API Endpoints

### Authentication

#### Register User

```
POST /auth/register
Content-Type: application/json

{
  "email": "farmer@example.com",
  "password": "SecurePassword123!"
}

Response: 201 Created
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "farmer@example.com",
  "created_at": "2025-01-15T10:30:00Z"
}
```

#### Login

```
POST /auth/login
Content-Type: application/x-www-form-urlencoded

email=farmer@example.com&password=SecurePassword123!

Response: 200 OK
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### Logout

```
POST /auth/logout
Authorization: Bearer <access_token>

Response: 200 OK
{
  "message": "Successfully logged out"
}
```

---

### Users

#### Get Current User

```
GET /users/me
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "farmer@example.com",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-15T10:30:00Z"
}
```

#### Update User

```
PUT /users/me
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "email": "newemail@example.com"
}

Response: 200 OK
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "newemail@example.com",
  "updated_at": "2025-01-16T14:20:00Z"
}
```

---

### Farmer Profiles

#### Get Farmer Profile

```
GET /farmer-profile
Authorization: Bearer <access_token>

Response: 200 OK
{
  "id": "650e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Rajesh Kumar",
  "phone": "9876543210",
  "state": "Punjab",
  "district": "Ludhiana",
  "village": "Samrala",
  "postal_code": "141121",
  "latitude": 30.8857,
  "longitude": 75.9064,
  "bio": "Wheat and rice farmer",
  "created_at": "2025-01-15T10:30:00Z",
  "updated_at": "2025-01-16T14:20:00Z"
}
```

#### Create/Update Farmer Profile

```
POST /farmer-profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "Rajesh Kumar",
  "phone": "9876543210",
  "state": "Punjab",
  "district": "Ludhiana",
  "village": "Samrala",
  "postal_code": "141121",
  "latitude": 30.8857,
  "longitude": 75.9064,
  "bio": "Wheat and rice farmer"
}

Response: 201 Created or 200 OK
{
  "id": "650e8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "full_name": "Rajesh Kumar",
  ...
}
```

---

### Commodities

#### List All Commodities

```
GET /commodities?category=Vegetables&limit=20&offset=0

Response: 200 OK
{
  "total": 45,
  "items": [
    {
      "id": "750e8400-e29b-41d4-a716-446655440010",
      "name": "Tomato",
      "category": "Vegetables",
      "unit": "kg",
      "description": "Fresh tomatoes",
      "icon_url": "https://..."
    },
    ...
  ]
}
```

**Query Parameters:**
- `category` (string, optional) – Filter by category (Cereals, Vegetables, Fruits, Spices)
- `limit` (int, default 20) – Number of results per page
- `offset` (int, default 0) – Pagination offset

#### Get Commodity Details

```
GET /commodities/750e8400-e29b-41d4-a716-446655440010

Response: 200 OK
{
  "id": "750e8400-e29b-41d4-a716-446655440010",
  "name": "Tomato",
  "category": "Vegetables",
  "unit": "kg",
  "description": "Fresh tomatoes",
  "icon_url": "https://..."
}
```

---

### Markets

#### List Markets

```
GET /markets?state=Punjab&district=Ludhiana&limit=20

Response: 200 OK
{
  "total": 5,
  "items": [
    {
      "id": "850e8400-e29b-41d4-a716-446655440000",
      "name": "Ludhiana Central Market",
      "state": "Punjab",
      "district": "Ludhiana",
      "village": "Ludhiana City",
      "market_type": "APMC",
      "latitude": 30.9010,
      "longitude": 75.8573,
      "contact_phone": "0161-2500123",
      "website_url": "https://..."
    },
    ...
  ]
}
```

**Query Parameters:**
- `state` (string, required) – State name
- `district` (string, optional) – District name
- `limit` (int, default 20)
- `offset` (int, default 0)

#### Get Market Details

```
GET /markets/850e8400-e29b-41d4-a716-446655440000

Response: 200 OK
{
  "id": "850e8400-e29b-41d4-a716-446655440000",
  "name": "Ludhiana Central Market",
  "state": "Punjab",
  "district": "Ludhiana",
  "village": "Ludhiana City",
  "market_type": "APMC",
  "latitude": 30.9010,
  "longitude": 75.8573,
  "contact_phone": "0161-2500123",
  "website_url": "https://..."
}
```

---

### Market Prices

#### Get Prices (with Filters)

```
GET /market-prices?state=Punjab&commodity_id=750e8400-e29b-41d4-a716-446655440010&date=2025-01-15

Response: 200 OK
{
  "total": 3,
  "items": [
    {
      "id": "950e8400-e29b-41d4-a716-446655440002",
      "market_id": "850e8400-e29b-41d4-a716-446655440000",
      "market_name": "Ludhiana Central Market",
      "commodity_id": "750e8400-e29b-41d4-a716-446655440010",
      "commodity_name": "Tomato",
      "price_date": "2025-01-15",
      "min_price": 20.00,
      "max_price": 28.00,
      "modal_price": 24.00,
      "quantity_traded": 560.0,
      "source": "Sample Data",
      "last_updated": "2025-01-15T08:00:00Z"
    },
    ...
  ]
}
```

**Query Parameters:**
- `state` (string, optional)
- `district` (string, optional)
- `market_id` (string, optional)
- `commodity_id` (string, optional)
- `date` (date, optional) – Format: YYYY-MM-DD
- `date_from` (date, optional)
- `date_to` (date, optional)
- `limit` (int, default 20)
- `offset` (int, default 0)

#### Compare Prices Across Markets

```
GET /market-prices/compare?commodity_id=750e8400-e29b-41d4-a716-446655440010&state=Punjab&date=2025-01-15

Response: 200 OK
{
  "commodity_id": "750e8400-e29b-41d4-a716-446655440010",
  "commodity_name": "Tomato",
  "date": "2025-01-15",
  "prices": [
    {
      "market_id": "850e8400-e29b-41d4-a716-446655440000",
      "market_name": "Ludhiana Central Market",
      "state": "Punjab",
      "district": "Ludhiana",
      "modal_price": 24.00,
      "min_price": 20.00,
      "max_price": 28.00,
      "quantity_traded": 560.0
    },
    {
      "market_id": "850e8400-e29b-41d4-a716-446655440001",
      "market_name": "Samrala Market",
      "state": "Punjab",
      "district": "Ludhiana",
      "modal_price": 26.00,
      "min_price": 22.00,
      "max_price": 30.00,
      "quantity_traded": 420.0
    }
  ]
}
```

**Query Parameters:**
- `commodity_id` (string, required)
- `state` (string, optional)
- `district` (string, optional)
- `date` (date, optional)

#### Get Historical Price Trend

```
GET /market-prices/history?market_id=850e8400-e29b-41d4-a716-446655440000&commodity_id=750e8400-e29b-41d4-a716-446655440010&days=30

Response: 200 OK
{
  "market_id": "850e8400-e29b-41d4-a716-446655440000",
  "market_name": "Ludhiana Central Market",
  "commodity_id": "750e8400-e29b-41d4-a716-446655440010",
  "commodity_name": "Tomato",
  "trend": [
    {
      "date": "2025-01-15",
      "min_price": 20.00,
      "max_price": 28.00,
      "modal_price": 24.00
    },
    {
      "date": "2025-01-14",
      "min_price": 19.50,
      "max_price": 27.50,
      "modal_price": 23.50
    },
    ...
  ]
}
```

**Query Parameters:**
- `market_id` (string, required)
- `commodity_id` (string, required)
- `days` (int, default 30) – Number of days to look back

---

### Saved Markets

#### Get Saved Markets

```
GET /saved-markets
Authorization: Bearer <access_token>

Response: 200 OK
{
  "total": 2,
  "items": [
    {
      "id": "afe8400-e29b-41d4-a716-446655440000",
      "market_id": "850e8400-e29b-41d4-a716-446655440000",
      "market_name": "Ludhiana Central Market",
      "state": "Punjab",
      "district": "Ludhiana",
      "saved_at": "2025-01-10T12:00:00Z"
    },
    ...
  ]
}
```

#### Save a Market

```
POST /saved-markets/850e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <access_token>

Response: 201 Created
{
  "id": "afe8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "market_id": "850e8400-e29b-41d4-a716-446655440000",
  "saved_at": "2025-01-15T14:30:00Z"
}
```

#### Unsave a Market

```
DELETE /saved-markets/850e8400-e29b-41d4-a716-446655440000
Authorization: Bearer <access_token>

Response: 204 No Content
```

---

### Saved Commodities

#### Get Saved Commodities

```
GET /saved-commodities
Authorization: Bearer <access_token>

Response: 200 OK
{
  "total": 3,
  "items": [
    {
      "id": "bfe8400-e29b-41d4-a716-446655440000",
      "commodity_id": "750e8400-e29b-41d4-a716-446655440010",
      "commodity_name": "Tomato",
      "category": "Vegetables",
      "saved_at": "2025-01-10T12:00:00Z"
    },
    ...
  ]
}
```

#### Save a Commodity

```
POST /saved-commodities/750e8400-e29b-41d4-a716-446655440010
Authorization: Bearer <access_token>

Response: 201 Created
{
  "id": "bfe8400-e29b-41d4-a716-446655440000",
  "user_id": "550e8400-e29b-41d4-a716-446655440000",
  "commodity_id": "750e8400-e29b-41d4-a716-446655440010",
  "saved_at": "2025-01-15T14:30:00Z"
}
```

#### Unsave a Commodity

```
DELETE /saved-commodities/750e8400-e29b-41d4-a716-446655440010
Authorization: Bearer <access_token>

Response: 204 No Content
```

---

## Error Responses

All error responses follow this format:

```json
{
  "detail": "Error message or list of validation errors",
  "status_code": 400
}
```

### Common Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK – Request succeeded |
| 201 | Created – Resource created successfully |
| 204 | No Content – Successful deletion |
| 400 | Bad Request – Invalid input |
| 401 | Unauthorized – Missing or invalid token |
| 403 | Forbidden – User doesn't have permission |
| 404 | Not Found – Resource not found |
| 409 | Conflict – Duplicate resource (e.g., market already saved) |
| 500 | Internal Server Error – Server error |

---

## API Documentation

When the backend is running, access interactive documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

---

## Rate Limiting (Future)

Rate limits may be implemented in production:

- Public endpoints: 100 requests/hour per IP
- Authenticated endpoints: 1000 requests/hour per user
- Headers will include `X-RateLimit-Limit` and `X-RateLimit-Remaining`

---

## Pagination

List endpoints use offset-based pagination:

```
GET /commodities?limit=20&offset=0

Response includes:
- total: Total number of items
- items: Array of results
```

---

## Sorting (Future)

Endpoints will support sorting:

```
GET /market-prices?sort_by=modal_price&order=desc
```

---

## Version Support

Current API Version: **v1** (indicated by `/api/v1/` prefix, optional in Phase 1)

Future versions will be at `/api/v2/`, maintaining backward compatibility.
