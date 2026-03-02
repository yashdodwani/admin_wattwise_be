# WattWise Admin Portal - API Documentation

## Overview

FastAPI-based authentication and admin management system for the WattWise Admin Portal.

**Frontend Reference:** https://meter-zen-portal.lovable.app

---

## Project Structure

```
admin_wattwise_be/
├── main.py                    # FastAPI application entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment configuration template
│
├── models/                   # SQLAlchemy ORM models
│   ├── __init__.py
│   └── admin.py             # Admin user database model
│
├── schemas/                  # Pydantic request/response schemas
│   ├── __init__.py
│   ├── models.py            # (existing file)
│   └── admin_schema.py      # Admin authentication schemas
│
├── routes/                   # FastAPI route handlers
│   ├── __init__.py
│   ├── auth.py              # (existing file - can be removed)
│   └── admin_auth.py        # Admin authentication endpoints
│
├── utils/                    # Utility functions
│   ├── __init__.py
│   ├── password.py          # Password hashing & generation
│   ├── jwt_handler.py       # JWT token creation & validation
│   ├── otp_helper.py        # OTP generation & verification
│   └── dependencies.py      # FastAPI dependency injection
│
└── config/                   # Configuration modules
    ├── __init__.py
    └── database.py          # SQLAlchemy engine setup
```

---

## Installation & Setup

### 1. Prerequisites
- Python 3.8+
- PostgreSQL (or SQLite for development)
- pip or conda

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Setup

Copy `.env.example` to `.env` and update values:

```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://admin:password@localhost:5432/wattwise_admin
SECRET_KEY=<generate-with-openssl-rand-hex-32>
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

### 4. Initialize Database

```bash
python -c "from config.database import init_db; init_db()"
```

### 5. Run the Application

```bash
python main.py
```

The API will be available at: `http://localhost:8000`

---

## API Endpoints

### Health Check

```
GET /health
```

Returns server status.

---

### Admin Authentication

#### 1. Register Admin

```
POST /admin/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": "1234567890",
  "descom_name": "Power Company A",
  "is_active": true
}
```

**Response (201 Created):**
```json
{
  "admin_id": "ADM123456",
  "generated_password": "Secure@Pass123",
  "message": "Admin registered successfully...",
  "email": "john@example.com"
}
```

**Error Cases:**
- 400: Email already registered
- 422: Validation error

---

#### 2. Login Admin

```
POST /admin/login
Content-Type: application/json

{
  "admin_id": "ADM123456",
  "password": "Secure@Pass123"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

**Error Cases:**
- 401: Invalid admin_id or password
- 403: Admin account inactive

---

#### 3. Forgot Password (Request OTP)

```
POST /admin/forgot-password
Content-Type: application/json

{
  "email": "john@example.com"
}
```

**Response (200 OK):**
```json
{
  "message": "OTP sent to john@example.com. Valid for 10 minutes.",
  "expires_in": 600
}
```

**Note:** In TEST MODE, OTP is printed to console. In production, integrate email service.

---

#### 4. Verify OTP & Reset Password

```
POST /admin/verify-otp
Content-Type: application/json

{
  "email": "john@example.com",
  "otp": "123456",
  "new_password": "NewSecure@Pass123"
}
```

**Response (200 OK):**
```json
{
  "message": "Password reset successfully. You can now log in with your new password."
}
```

**Error Cases:**
- 400: Invalid OTP, OTP expired, max attempts exceeded
- 404: Email not found

---

#### 5. Get Admin Profile (Protected)

```
GET /admin/profile
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "admin_id": "ADM123456",
  "name": "John Doe",
  "email": "john@example.com",
  "phone_number": "1234567890",
  "descom_name": "Power Company A",
  "is_active": true,
  "created_at": "2026-03-03T10:30:00"
}
```

**Error Cases:**
- 401: Missing or invalid token
- 403: Admin inactive

---

#### 6. Logout (Protected)

```
POST /admin/logout
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Admin ADM123456 logged out successfully"
}
```

---

## Authentication

### JWT Bearer Token

All protected endpoints require a Bearer token:

```
Authorization: Bearer <access_token>
```

**Token Details:**
- Algorithm: HS256
- Expiry: 60 minutes (configurable)
- Payload:
  ```json
  {
    "admin_id": "ADM123456",
    "role": "admin",
    "email": "john@example.com",
    "exp": 1234567890
  }
  ```

---

## Security Features

### 1. Password Security
- **Hashing:** bcrypt (passlib)
- **Generation:** Secure 12-character passwords with mixed character types
- **Salting:** Automatic with bcrypt

### 2. JWT Tokens
- **Algorithm:** HS256
- **Expiry:** Configurable (default: 60 minutes)
- **Payload:** admin_id, role, email, expiry

### 3. OTP System
- **Generation:** Cryptographically secure 6-digit OTP
- **Storage:** In-memory (Redis in production)
- **Expiry:** 10 minutes
- **Attempts:** Max 3 attempts per OTP

### 4. Database
- **ORM:** SQLAlchemy
- **Type:** PostgreSQL (recommended)
- **Constraints:** Unique email, unique admin_id, indexed fields

### 5. CORS
- **Allowed Origins:** localhost, production frontend
- **Methods:** GET, POST, PUT, DELETE, OPTIONS
- **Credentials:** Enabled

---

## Database Schema

### Admin Table

```sql
CREATE TABLE admins (
  id SERIAL PRIMARY KEY,
  admin_id VARCHAR(10) UNIQUE NOT NULL,
  name VARCHAR(255) NOT NULL,
  email VARCHAR(255) UNIQUE NOT NULL,
  phone_number VARCHAR(15) NOT NULL,
  descom_name VARCHAR(255) NOT NULL,
  hashed_password VARCHAR(255) NOT NULL,
  is_active BOOLEAN DEFAULT true,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  otp_code VARCHAR(6),
  otp_expiry TIMESTAMP
);

CREATE INDEX idx_admin_id ON admins(admin_id);
CREATE INDEX idx_email ON admins(email);
CREATE INDEX idx_is_active ON admins(is_active);
```

---

## File Descriptions

### Models

**`models/admin.py`**
- SQLAlchemy ORM model for admin users
- Columns: id, admin_id, name, email, phone_number, descom_name, hashed_password, is_active, timestamps, OTP fields
- Relationships: (extensible for future features)

### Schemas

**`schemas/admin_schema.py`**
- Pydantic models for request/response validation
- Models: AdminRegisterRequest, AdminLoginRequest, TokenResponse, ForgotPasswordRequest, VerifyOTPRequest, AdminResponse

### Routes

**`routes/admin_auth.py`**
- FastAPI route handlers
- Endpoints: /register, /login, /forgot-password, /verify-otp, /profile, /logout
- Business logic: validation, hashing, JWT generation, OTP management

### Utilities

**`utils/password.py`**
- `hash_password()`: Hash password with bcrypt
- `verify_password()`: Verify password against hash
- `generate_secure_password()`: Generate 12-character secure password
- `generate_otp()`: Generate 6-digit OTP

**`utils/jwt_handler.py`**
- `create_access_token()`: Create JWT token
- `verify_token()`: Decode and validate JWT
- `get_token_expiry_seconds()`: Get token expiry duration

**`utils/otp_helper.py`**
- `send_otp_email()`: Mock email function (integrate with SendGrid, SES, etc.)
- `store_otp()`: Store OTP temporarily
- `verify_otp()`: Validate OTP with expiry and attempt tracking
- `invalidate_otp()`: Remove OTP after use or expiry

**`utils/dependencies.py`**
- `get_db()`: Database session dependency
- `get_current_admin()`: Current authenticated admin dependency
- `verify_admin_role()`: Admin role verification (extensible)

### Config

**`config/database.py`**
- SQLAlchemy engine initialization
- Session factory setup
- Database initialization function
- Database cleanup function (for testing)

---

## Testing the API

### Using cURL

```bash
# Health check
curl http://localhost:8000/health

# Register admin
curl -X POST http://localhost:8000/admin/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "1234567890",
    "descom_name": "Power Company A"
  }'

# Login
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "ADM123456",
    "password": "generated_password"
  }'

# Get profile (replace TOKEN with actual access_token)
curl http://localhost:8000/admin/profile \
  -H "Authorization: Bearer TOKEN"
```

### Using FastAPI Docs

Visit: `http://localhost:8000/docs`

Interactive Swagger UI for testing all endpoints.

---

## Production Deployment Checklist

- [ ] Update `SECRET_KEY` with a secure random value
- [ ] Configure PostgreSQL database URL
- [ ] Set up SMTP server for OTP emails
- [ ] Implement Redis for OTP storage (replace in-memory)
- [ ] Enable HTTPS/SSL
- [ ] Configure CORS allowed origins
- [ ] Set up monitoring and logging
- [ ] Implement rate limiting
- [ ] Add database connection pooling
- [ ] Set up CI/CD pipeline
- [ ] Configure environment variables
- [ ] Add database backups
- [ ] Implement token blacklist for logout
- [ ] Add audit logging

---

## Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt
```

### Database connection error
```bash
# Check PostgreSQL is running
# Verify DATABASE_URL in .env
python -c "from config.database import engine; print(engine.connect())"
```

### JWT token invalid
- Check SECRET_KEY matches between token creation and validation
- Verify token hasn't expired
- Check Authorization header format: `Bearer <token>`

### OTP not received (in development)
- OTP printed to console in TEST MODE
- Check application logs
- Implement email service for production

---

## Future Enhancements

1. **Token Blacklist:** Implement token revocation for logout
2. **Redis Integration:** Replace in-memory OTP storage
3. **Email Service:** Integrate SendGrid, AWS SES, or Gmail SMTP
4. **2FA:** Add two-factor authentication
5. **Audit Logging:** Log all admin actions
6. **Rate Limiting:** Add rate limits to endpoints
7. **IP Whitelisting:** Restrict admin access by IP
8. **Session Management:** Track active sessions
9. **Activity Tracking:** Log login/logout history
10. **Notifications:** Email notifications for suspicious activity

---

## Support & Contribution

For issues, questions, or contributions, please refer to the project repository.

---

**Last Updated:** March 3, 2026
**Version:** 1.0.0
**Project:** WattWise Admin Portal

