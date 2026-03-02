# WattWise Admin Portal - Quick Start Guide

## ⚡ Get Running in 5 Minutes

### Step 1: Install Dependencies (1 min)
```bash
pip install -r requirements.txt
```

### Step 2: Configure Environment (1 min)
```bash
cp .env.example .env
```

Edit `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost/wattwise_admin
SECRET_KEY=<your-secret-key>
```

### Step 3: Initialize Database (1 min)
```bash
python -c "from config.database import init_db; init_db()"
```

### Step 4: Start Server (1 min)
```bash
python main.py
```

### Step 5: Access API (1 min)
Visit: **http://localhost:8000/docs**

---

## 🧪 Quick Test

### Register Admin
```bash
curl -X POST http://localhost:8000/admin/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "phone_number": "1234567890",
    "descom_name": "Power Company A"
  }'
```

Response:
```json
{
  "admin_id": "ADM123456",
  "generated_password": "SecurePass@123",
  "email": "john@example.com",
  "message": "Admin registered successfully..."
}
```

### Login
```bash
curl -X POST http://localhost:8000/admin/login \
  -H "Content-Type: application/json" \
  -d '{
    "admin_id": "ADM123456",
    "password": "SecurePass@123"
  }'
```

Response:
```json
{
  "access_token": "eyJhbGc...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### Access Profile
```bash
curl http://localhost:8000/admin/profile \
  -H "Authorization: Bearer eyJhbGc..."
```

---

## 📚 Next Steps

1. **Read Full API Documentation:** [README.md](README.md)
2. **Understand Architecture:** [IMPLEMENTATION.md](IMPLEMENTATION.md)
3. **Deploy to Production:** [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Check All Tasks:** [DELIVERY_CHECKLIST.md](DELIVERY_CHECKLIST.md)

---

## 🆘 Troubleshooting

### "Module not found" Error
```bash
pip install -r requirements.txt
```

### Database Connection Error
1. Check PostgreSQL is running
2. Verify DATABASE_URL in `.env`
3. Check database exists

### Port 8000 Already in Use
```bash
python main.py --port 8001
```

### OTP Not Sending
- In development, OTP is printed to console
- In production, integrate email service

---

**👉 Visit http://localhost:8000/docs to test endpoints!**

