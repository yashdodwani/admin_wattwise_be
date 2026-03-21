# WattWise Admin Portal API Documentation

This documentation provides details on the API endpoints for the WattWise Admin Portal backend.

## Base URL
`/` (e.g., `http://localhost:8000` or `https://your-render-url.onrender.com`)

## Authentication
Most endpoints are protected and require a Bearer Token.
After logging in, include the token in the `Authorization` header:

```
Authorization: Bearer <your_access_token>
```

---

## 1. Admin Authentication
**Prefix**: `/admin`

### Register Admin
*   **Method**: `POST`
*   **Path**: `/admin/register`
*   **Description**: Register a new admin user.
*   **Request Body**:
    ```json
    {
      "name": "John Doe",
      "email": "john@example.com",
      "phone_number": "1234567890"
    }
    ```
*   **Response**:
    ```json
    {
      "message": "Registration successful",
      "admin_id": "ADM1023",
      "password": "Secure@Pass1"
    }
    ```

### Login
*   **Method**: `POST`
*   **Path**: `/admin/login`
*   **Description**: Authenticate and get a JWT token.
*   **Request Body**:
    ```json
    {
      "admin_id": "ADM123456",
      "password": "Secure@Pass123"
    }
    ```
*   **Response**:
    ```json
    {
      "access_token": "eyJhbGciOi...",
      "token_type": "bearer",
      "expires_in": 3600
    }
    ```

### Forgot Password (OTP)
*   **Method**: `POST`
*   **Path**: `/admin/forgot-password`
*   **Description**: Request an OTP for password reset.
*   **Request Body**:
    ```json
    {
      "email": "john@example.com"
    }
    ```
*   **Response**:
    ```json
    {
      "message": "OTP sent to john@example.com. Valid for 10 minutes.",
      "expires_in": 600
    }
    ```

### Verify OTP & Reset Password
*   **Method**: `POST`
*   **Path**: `/admin/verify-otp`
*   **Description**: Verify OTP and set a new password.
*   **Request Body**:
    ```json
    {
      "email": "john@example.com",
      "otp": "123456",
      "new_password": "NewSecure@Pass123"
    }
    ```
*   **Response**:
    ```json
    {
      "message": "Password reset successfully. You can now log in with your new password."
    }
    ```

### Get Profile
*   **Method**: `GET`
*   **Path**: `/admin/profile`
*   **Description**: Get current logged-in admin's profile.
*   **Response**: `AdminResponse` object (see Schema).

### Logout
*   **Method**: `POST`
*   **Path**: `/admin/logout`
*   **Description**: Log out the current admin.
*   **Response**: `{"message": "Admin ... logged out successfully"}`

---

## 2. Dashboard
**Prefix**: `/api/dashboard`

### Dashboard Stats
*   **Method**: `GET`
*   **Path**: `/api/dashboard/stats`
*   **Description**: Get KPI statistics for the dashboard.
*   **Response**:
    ```json
    {
      "total_users": 150,
      "active_meters": 145,
      "total_revenue": 50000.0,
      "total_complaints": 12,
      "overdue_bills": 5,
      "recharge_volume": 320
    }
    ```

### Complaint Status Distribution
*   **Method**: `GET`
*   **Path**: `/api/dashboard/complaints-status`
*   **Description**: Get counts of complaints grouped by status.
*   **Response**: `[{"status": "open", "count": 5}, ...]`

---

## 3. Users Management
**Prefix**: `/api/users`

### List Users
*   **Method**: `GET`
*   **Path**: `/api/users/`
*   **Query Params**:
    *   `state`: Filter by state name
    *   `discom`: Filter by DISCOM name
    *   `active`: Filter by active status (true/false)
    *   `amount_gt`: Filter by bill amount greater than X
*   **Response**: List of `UserResponse` objects.

### Get User Details
*   **Method**: `GET`
*   **Path**: `/api/users/{id}`
*   **Description**: Get details of a specific user by UUID.
*   **Response**: `UserResponse` object.

### Update User
*   **Method**: `PUT`
*   **Path**: `/api/users/{id}`
*   **Request Body**:
    ```json
    {
      "name": "New Name",
      "phone": "9876543210",
      "state": "Maharashtra",
      "discom": "MSEDCL"
    }
    ```
*   **Response**: Updated `UserResponse` object.

### Toggle Active Status
*   **Method**: `PATCH`
*   **Path**: `/api/users/{id}/toggle-active`
*   **Description**: Toggle a user's `is_active` status.
*   **Response**: Updated `UserResponse` object.

### Get User Balance
*   **Method**: `GET`
*   **Path**: `/api/users/{id}/balance`
*   **Query Params**: `period` (e.g., "current_month")
*   **Response**: `{"user_id": "...", "remaining_balance": 100.0, ...}`

---

## 4. Complaints
**Prefix**: `/api/complaints`

### List Complaints
*   **Method**: `GET`
*   **Path**: `/api/complaints/`
*   **Query Params**:
    *   `status`: Filter by status (Open, In Progress, Resolved)
    *   `priority`: Filter by priority (High, Medium, Low)
*   **Response**: List of `ComplaintResponse` objects.

### Get Complaint Details
*   **Method**: `GET`
*   **Path**: `/api/complaints/{id}`
*   **Response**: `ComplaintResponse` object.

### Update Complaint Status
*   **Method**: `PATCH`
*   **Path**: `/api/complaints/{id}/status`
*   **Request Body**:
    ```json
    {
      "status": "Resolved"
    }
    ```
*   **Response**: Updated `ComplaintResponse` object.

### Add Note
*   **Method**: `POST`
*   **Path**: `/api/complaints/{id}/notes`
*   **Query Params**: `note` (string)
*   **Response**: `{"message": "Note added successfully", "note": "..."}`

---

## 5. Revenue & Transactions
**Prefix**: `/api`

### List Transactions
*   **Method**: `GET`
*   **Path**: `/api/transactions`
*   **Query Params**:
    *   `page`: Page number (default 1)
    *   `page_size`: Items per page (default 20)
    *   `date_from`: Start date (ISO 8601)
    *   `date_to`: End date (ISO 8601)
    *   `payment_method`: Filter by method (UPI, Card, etc.)
    *   `status`: Filter by status (Success, Pending, Failed)
*   **Response**:
    ```json
    {
      "total": 100,
      "page": 1,
      "page_size": 20,
      "data": [ ... ]
    }
    ```

### Revenue Summary
*   **Method**: `GET`
*   **Path**: `/api/revenue/summary`
*   **Response**:
    ```json
    {
      "total_revenue": 100000.0,
      "pending_revenue": 5000.0,
      "average_bill_amount": 1200.0,
      "highest_payment": 5000.0
    }
    ```

### Revenue by State
*   **Method**: `GET`
*   **Path**: `/api/revenue/by-state`
*   **Response**: `[{"state": "Delhi", "revenue": 50000}, ...]`

### Monthly Revenue (Last 6 Months)
*   **Method**: `GET`
*   **Path**: `/api/revenue/monthly`
*   **Response**: `[{"month": "Jan", "revenue": 12000}, ...]`

### Payment Method Distribution
*   **Method**: `GET`
*   **Path**: `/api/revenue/payment-methods`
*   **Response**: `[{"payment_method": "UPI", "count": 50, "total_amount": 20000}, ...]`

---

## 6. SMS & Notifications
**Prefix**: `/api/sms`

### List SMS Logs
*   **Method**: `GET`
*   **Path**: `/api/sms/logs`
*   **Query Params**: `page` (default 1), `page_size` (default 20)
*   **Response**: List of `SMSLogResponse` objects.

### Send Single SMS
*   **Method**: `POST`
*   **Path**: `/api/sms/send`
*   **Request Body**:
    ```json
    {
      "user_id": "USR123",
      "phone_number": "9876543210",
      "message": "Hello from WattWise"
    }
    ```
*   **Response**: `SendSMSResponse` object.

### Send Bulk SMS
*   **Method**: `POST`
*   **Path**: `/api/sms/send-bulk`
*   **Request Body**:
    ```json
    {
      "category": "overdue", 
      "message": "Please pay your bill",
      "user_ids": [] 
    }
    ```
    *   `category`: "overdue", "pending", or "selected_users".
    *   `user_ids`: Required only if category is "selected_users".
*   **Response**: `{"sent": 10, "failed": 0, "total": 10}`

### Retry SMS
*   **Method**: `POST`
*   **Path**: `/api/sms/retry/{id}`
*   **Description**: Retry a failed SMS by ID.

---

## 7. Settings
**Prefix**: `/api`

### Get Billing Settings
*   **Method**: `GET`
*   **Path**: `/api/settings/billing`
*   **Response**:
    ```json
    {
      "billing_cycle_days": 30,
      "late_fee_amount": 50.0,
      "grace_period_days": 5,
      "auto_disconnect_enabled": true
    }
    ```

### Update Billing Settings
*   **Method**: `PUT`
*   **Path**: `/api/settings/billing`
*   **Request Body**: Same as response.

### Get Admin Profile (Settings)
*   **Method**: `GET`
*   **Path**: `/api/admin/profile`
*   **Response**: `AdminProfileResponse`

### Update Admin Profile
*   **Method**: `PUT`
*   **Path**: `/api/admin/profile`
*   **Request Body**:
    ```json
    {
      "name": "New Name",
      "phone_number": "...",
      "password": "NewPassword" 
    }
    ```

### Get Notification Preferences
*   **Method**: `GET`
*   **Path**: `/api/settings/notifications`
*   **Response**:
    ```json
    {
      "sms_alerts_enabled": true,
      "email_alerts_enabled": true,
      "outage_notifications": true,
      "billing_notifications": true
    }
    ```

### Update Notification Preferences
*   **Method**: `PUT`
*   **Path**: `/api/settings/notifications`
*   **Request Body**: Same as response.

---

## 8. Reference Data
**Prefix**: `/api`

### List States
*   **Method**: `GET`
*   **Path**: `/api/states`
*   **Response**: `[{"id": 1, "name": "Andhra Pradesh"}, ...]`

### List DISCOMs
*   **Method**: `GET`
*   **Path**: `/api/discoms`
*   **Query Params**: `state_id` (optional)
*   **Response**: `[{"id": 1, "name": "APEPDCL", "state": "Andhra Pradesh"}, ...]`

