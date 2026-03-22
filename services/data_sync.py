
import asyncio
import logging
import os
import uuid
from datetime import datetime
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from config.database import SessionLocal, engine as admin_engine
from models.user import User
from models.complaint import Complaint, Status, Priority
from models.transaction import Transaction

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# User DB Connection
USER_DB_URL = os.getenv("user_db_url")

def get_user_db_connection():
    if not USER_DB_URL:
        logger.error("user_db_url not set in .env")
        return None
    try:
        engine = create_engine(USER_DB_URL)
        return engine.connect()
    except Exception as e:
        logger.error(f"Failed to connect to User DB: {e}")
        return None

def sync_data():
    """
    Synchronizes users and complaints from User Portal DB to Admin Portal DB.
    """
    logger.info("Starting data synchronization...")
    
    user_conn = get_user_db_connection()
    if not user_conn:
        return

    admin_db: Session = SessionLocal()

    try:
        # 1. Fetch Users from User DB with joined data
        # We join meters to get meter_id. 
        # We join bills to get latest bill info (simplified aggregation).
        # We join complaints to seeing active status (simplified aggregation).
        
        # Taking a simpler approach: fetch users first, then fetch related data if needed or do subqueries.
        # Given the schema, let's just fetch users and then iterate.
        
        users_query = text("""
            SELECT 
                u.id, u.name, u.username, u.phone_number, u.consumer_number, 
                u.is_active, u.created_at, u.location, u.discom
            FROM users u
        """)
        
        user_rows = user_conn.execute(users_query).fetchall()
        
        logger.info(f"Found {len(user_rows)} users in User DB.")

        for row in user_rows:
            try:
                # Extract User Data
                user_portal_id = row.id
                name = row.name
                email = row.username # Assuming username is email? or just username.
                phone = row.phone_number
                consumer_no = row.consumer_number
                is_active = row.is_active
                created_at = row.created_at
                location = row.location
                discom = row.discom
                
                # Fetch Meter ID
                meter_query = text("SELECT id FROM meters WHERE user_id = :uid LIMIT 1")
                meter_row = user_conn.execute(meter_query, {"uid": user_portal_id}).fetchone()
                meter_id = str(meter_row.id) if meter_row else f"METER_{consumer_no}"

                # Fetch Bill Info (Simplification: Total Unpaid Amount)
                bill_query = text("SELECT COALESCE(SUM(amount), 0) FROM bills WHERE user_id = :uid AND status != 'Paid'")
                bill_amount = user_conn.execute(bill_query, {"uid": user_portal_id}).scalar() or 0.0

                # Check Active Complaint
                complaint_check_query = text("SELECT id FROM complaints WHERE user_id = :uid AND status != 'Resolved' LIMIT 1")
                active_complaint_row = user_conn.execute(complaint_check_query, {"uid": user_portal_id}).fetchone()
                has_active_complaint = active_complaint_row is not None
                active_complaint_id_str = str(active_complaint_row.id) if active_complaint_row else None

                # Generate IDs for Admin DB
                # We use consumer_no as the stable key to find existing user
                existing_user = admin_db.query(User).filter(User.consumer_id == consumer_no).first()

                if existing_user:
                    # Update existing user
                    existing_user.name = name
                    existing_user.phone = phone
                    existing_user.state = location or "Unknown"
                    existing_user.discom = discom or "Unknown"
                    existing_user.bill_amount = float(bill_amount)
                    existing_user.active_complaint = has_active_complaint
                    if active_complaint_id_str:
                        existing_user.complaint_id = f"CMP_{active_complaint_id_str}"
                    # Update other fields if necessary
                    # We don't overwrite created_at usually, but maybe updated_at if we had it.
                else:
                    # Create new user
                    new_user = User(
                        id=uuid.uuid4(),
                        user_id=f"user_{user_portal_id}", # Mapping ID
                        consumer_id=consumer_no,
                        name=name,
                        meter_id=meter_id,
                        phone=phone,
                        state=location or "Unknown",
                        discom=discom or "Unknown",
                        bill_amount=float(bill_amount),
                        remaining_balance=0.0, # Default
                        balance_used=0.0, # Default
                        active_complaint=has_active_complaint,
                        complaint_id=f"CMP_{active_complaint_id_str}" if active_complaint_id_str else None,
                        is_active=is_active if is_active is not None else True,
                        created_at=created_at or datetime.utcnow(),
                        last_payment_date=None 
                    )
                    admin_db.add(new_user)
                    admin_db.flush() # flush to get ID if needed, though we set UUID manually
                    existing_user = new_user # For complaint linking

                # 2. Sync Complaints for this user
                # Fetch complaints from User DB
                complaints_query = text("""
                    SELECT id, type, description, status, created_at, resolved_at 
                    FROM complaints 
                    WHERE user_id = :uid
                """)
                complaint_rows = user_conn.execute(complaints_query, {"uid": user_portal_id}).fetchall()

                for c_row in complaint_rows:
                    c_portal_id = c_row.id
                    c_type = c_row.type
                    c_desc = c_row.description
                    c_status_str = c_row.status
                    c_created_at = c_row.created_at
                    c_resolved_at = c_row.resolved_at

                    # Map Status
                    status_enum = Status.OPEN
                    if c_status_str == 'Resolved':
                        status_enum = Status.RESOLVED
                    elif c_status_str == 'In Progress':
                        status_enum = Status.IN_PROGRESS
                    
                    # Map Complaint ID
                    admin_complaint_id = f"CMP_{c_portal_id}"

                    # Check if exists
                    existing_complaint = admin_db.query(Complaint).filter(Complaint.complaint_id == admin_complaint_id).first()

                    if existing_complaint:
                        existing_complaint.status = status_enum
                        existing_complaint.description = c_desc
                        existing_complaint.updated_at = c_resolved_at if c_resolved_at else datetime.utcnow()
                    else:
                        new_complaint = Complaint(
                            id=uuid.uuid4(),
                            complaint_id=admin_complaint_id,
                            user_id=existing_user.id, # Link to Admin User UUID
                            issue_type=c_type or "General",
                            priority=Priority.MEDIUM, # Default
                            status=status_enum,
                            description=c_desc,
                            created_at=c_created_at or datetime.utcnow(),
                            updated_at=c_resolved_at
                        )
                        admin_db.add(new_complaint)
                
                admin_db.commit()

            except Exception as e:
                logger.error(f"Error syncing user {row.id}: {e}")
                admin_db.rollback()
                continue

    except Exception as e:
        logger.error(f"Global sync error: {e}")
    finally:
        user_conn.close()
        admin_db.close()
        logger.info("Data synchronization completed.")

if __name__ == "__main__":
    sync_data()

