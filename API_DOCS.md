# Leafman API Documentation

**Version:** 1.0
**Base URL:** `https://leafman.34.180.4.205.sslip.io`

This document provides a comprehensive guide to the Leafman Leave Management System API. The API is RESTful, uses JSON for all responses, and is secured using JWT Bearer tokens.

## Authentication

All protected endpoints require an `Authorization` header containing a JWT Bearer token.

To obtain a token, you must use the `/auth/token` endpoint.

### `POST /auth/token`

Exchanges a user's email and password for a JWT access token.

**Request (`Content-Type: application/x-www-form-urlencoded`)**

```bash
curl -X POST \
  "http://<BASE_URL>/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=hr@heywoah.com&password=your_password"
```

**Successful Response (200 OK)**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

## Employee Endpoints

These are the endpoints available to all authenticated users (both Employees and Admins).

### User Profile & Balances

#### `GET /users/me`
Retrieves the profile of the currently authenticated user.

- **Authentication:** Required.

**Example Request**
```bash
curl -X GET \
  "http://<BASE_URL>/users/me" \
  -H "Authorization: Bearer <your_token>"
```

**Sample Response**
```json
{
  "user_id": 2,
  "first_name": "Irish",
  "last_name": "Heywoah",
  "email": "arpit@heywoah.com",
  "department_id": 1,
  "join_date": "2025-08-14",
  "role": "Employee"
}
```

#### `GET /users/me/balances`
Retrieves the detailed leave balances for the currently authenticated user for the current year.

- **Authentication:** Required.

**Example Request**
```bash
curl -X GET \
  "http://<BASE_URL>/users/me/balances" \
  -H "Authorization: Bearer <your_token>"
```

**Sample Response**
```json
[
  {
    "leave_type": {
      "leave_type_id": 1,
      "name": "Casual Leave (CL)",
      "paid": true,
      "annual_quota": "12.00",
      "carry_forward": false
    },
    "year": 2025,
    "balance_days": "12.00",
    "used_days": "1.00"
  },
  {
    "leave_type": {
      "leave_type_id": 2,
      "name": "Earned Leave (EL)",
      "paid": true,
      "annual_quota": "15.00",
      "carry_forward": true
    },
    "year": 2025,
    "balance_days": "15.00",
    "used_days": "5.00"
  }
]
```

### Leave Requests (Employee)

#### `GET /leave-requests/types`
Retrieves a list of all available leave types in the system. This is useful for populating a dropdown menu before a user applies for leave.

- **Authentication:** Required.

**Example Request**
```bash
curl -X GET \
  "http://<BASE_URL>/leave-requests/types" \
  -H "Authorization: Bearer <your_token>"
```

**Sample Response**
```json
[
  {
    "leave_type_id": 1,
    "name": "Casual Leave (CL)",
    "paid": true,
    "annual_quota": "12.00",
    "carry_forward": false
  },
  {
    "leave_type_id": 2,
    "name": "Earned Leave (EL)",
    "paid": true,
    "annual_quota": "15.00",
    "carry_forward": true
  }
]
```

#### `POST /leave-requests/`
Submits a new leave request for the authenticated user.

- **Authentication:** Required.

**Request Body (JSON)**
```json
{
  "leave_type_id": 1,
  "start_date": "2025-12-22",
  "end_date": "2025-12-26",
  "reason": "Christmas vacation"
}
```

**Sample Response (201 Created)**
```json
{
  "request_id": 105,
  "user_id": 2,
  "leave_type": { "name": "Casual Leave (CL)", ... },
  "start_date": "2025-12-22",
  "end_date": "2025-12-26",
  "total_days": "5.00",
  "is_half_day": false,
  "status": "Pending",
  "reason": "Christmas vacation"
}
```

#### `GET /leave-requests/`
Retrieves a paginated list of the authenticated user's own leave request history.

- **Authentication:** Required.

**Example Request**
```bash
curl -X GET \
  "http://<BASE_URL>/leave-requests/" \
  -H "Authorization: Bearer <your_token>"
```

---

## Admin Endpoints

These endpoints are only available to users with the `Admin` role.

### User Management

#### `POST /admin/users`
Creates a new user in the system. When a user is created, their leave balances for the current year are automatically calculated and initialized.

- **Authentication:** Admin role required.

**Request Body (JSON)**
```json
{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@leafman.io",
  "password": "a_secure_password",
  "join_date": "2025-09-01",
  "role": "Employee",
  "department_id": 2
}
```

### Leave Request Management

#### `GET /admin/leave-requests`
Retrieves a list of all leave requests in the system. Can be filtered by status.

- **Authentication:** Admin role required.
- **Query Parameters:**
  - `status` (optional): Filter by `Pending`, `Approved`, or `Rejected`.
  - `page` (optional): For pagination.
  - `limit` (optional): For pagination.

**Example Request (Pending Leaves)**
```bash
curl -X GET \
  "http://<BASE_URL>/admin/leave-requests?status=Pending" \
  -H "Authorization: Bearer <admin_token>"
```

**Sample Response**
```json
[
  {
    "request_id": 105,
    "user": {
      "user_id": 2,
      "first_name": "Irish",
      "last_name": "Heywoah"
    },
    "leave_type": { "name": "Casual Leave (CL)", ... },
    "start_date": "2025-12-22",
    "end_date": "2025-12-26",
    "total_days": "5.00",
    "status": "Pending",
    "reason": "Christmas vacation"
  }
]
```

#### `PATCH /admin/leave-requests/{request_id}`
Approves or rejects a specific leave request.

- **Authentication:** Admin role required.

  **Request Body (JSON)**
  ```json
  {
    "status": "Approved",
    "approval_note": "Enjoy your time off!"
  }
  ```

### System Configuration

#### `GET /admin/departments/`
Lists all departments configured in the system.

- **Authentication:** Admin role required.

#### `POST /admin/departments`
Creates a new department.

- **Authentication:** Admin role required.
- **Request Body (JSON):** `{ "name": "Marketing" }`

#### `POST /admin/leave-types`
Creates a new type of leave available to all employees.

- **Authentication:** Admin role required.
- **Request Body (JSON):** `{ "name": "Sick Leave", "annual_quota": 10, "carry_forward": true }`