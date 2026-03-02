#!/usr/bin/env python
"""
Test script to verify all imports and basic functionality.
"""

import sys
import os

# Add project to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("=" * 60)
print("WATTWISE ADMIN PORTAL - IMPORT & DEPENDENCY TEST")
print("=" * 60)

# Test 1: Database config
print("\n[1/6] Testing config.database...")
try:
    from config.database import get_db, SessionLocal, engine, init_db
    print("✓ config.database imports OK")
except Exception as e:
    print(f"✗ config.database import failed: {e}")
    sys.exit(1)

# Test 2: Models
print("[2/6] Testing models.admin...")
try:
    from models.admin import Admin, Base
    print("✓ models.admin imports OK")
except Exception as e:
    print(f"✗ models.admin import failed: {e}")
    sys.exit(1)

# Test 3: Schemas
print("[3/6] Testing schemas.admin_schema...")
try:
    from schemas.admin_schema import (
        AdminRegisterRequest,
        AdminLoginRequest,
        TokenResponse,
        AdminResponse
    )
    print("✓ schemas.admin_schema imports OK")
except Exception as e:
    print(f"✗ schemas.admin_schema import failed: {e}")
    sys.exit(1)

# Test 4: Utils
print("[4/6] Testing utils modules...")
try:
    from utils.password import hash_password, verify_password, generate_secure_password, generate_otp
    print("  ✓ utils.password imports OK")

    from utils.jwt_handler import create_access_token, verify_token, get_token_expiry_seconds
    print("  ✓ utils.jwt_handler imports OK")

    from utils.otp_helper import send_otp_email, store_otp, verify_otp, invalidate_otp
    print("  ✓ utils.otp_helper imports OK")
except Exception as e:
    print(f"✗ utils import failed: {e}")
    sys.exit(1)

# Test 5: Dependencies
print("[5/6] Testing utils.dependencies...")
try:
    from utils.dependencies import get_db, get_current_admin, verify_admin_role
    print("✓ utils.dependencies imports OK")
except Exception as e:
    print(f"✗ utils.dependencies import failed: {e}")
    sys.exit(1)

# Test 6: Routes
print("[6/6] Testing routes.admin_auth...")
try:
    from routes.admin_auth import router
    print("✓ routes.admin_auth imports OK")
except Exception as e:
    print(f"✗ routes.admin_auth import failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("✓ ALL TESTS PASSED!")
print("=" * 60)
print("\nThe application is ready to run!")
print("Command: python main.py")
print("Then visit: http://localhost:8000/docs")

