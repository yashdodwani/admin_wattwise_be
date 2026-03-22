"""
Script to backfill the notifications table based on existing users, complaints, and transactions.
Run this script after running database migrations.
Usage:
    python -m scripts.seed_notifications
"""

import sys
import os
import random
from datetime import datetime, timedelta
from uuid import uuid4

# Add project root to sys path
sys.path.append(os.getcwd())

from config.database import SessionLocal
from models.user import User
from models.complaint import Complaint
from models.notification import Notification

def seed_notifications():
    db = SessionLocal()
    try:
        print("🔍 Checking for existing data...")
        users = db.query(User).all()
        complaints = db.query(Complaint).all()
        
        print(f"found {len(users)} users and {len(complaints)} complaints.")
        
        notifications = []
        
        # 1. Create notifications for recent complaints
        print("📝 Generating complaint notifications...")
        for complaint in complaints:
            # Check if notification already exists
            existing = db.query(Notification).filter(Notification.reference_id == str(complaint.id)).first()
            if existing:
                continue
                
            notif = Notification(
                id=uuid4(),
                title="Complaint Raised",
                message=f"New complaint {complaint.complaint_id} ({complaint.issue_type}) created.",
                type="complaint",
                reference_id=str(complaint.id),
                is_read=random.choice([True, False]),
                priority="high" if complaint.priority.value == "High" else "medium",
                created_at=complaint.created_at
            )
            notifications.append(notif)

        # 2. Create notifications for overdue users
        print("💰 Generating overdue bill notifications...")
        for user in users:
            if user.remaining_balance > 0:
                # Check for duplicate (simple check)
                existing = db.query(Notification).filter(
                    Notification.reference_id == str(user.id),
                    Notification.type == "billing"
                ).first()
                if existing:
                    continue

                notif = Notification(
                    id=uuid4(),
                    title="Bill Overdue",
                    message=f"User {user.name} ({user.consumer_id}) has an overdue balance of ₹{user.remaining_balance}",
                    type="billing",
                    reference_id=str(user.id),
                    is_read=False,
                    priority="high",
                    created_at=datetime.utcnow() - timedelta(hours=random.randint(1, 48))
                )
                notifications.append(notif)

        # 3. Add some system notifications
        print("⚙️ Generating system notifications...")
        system_msgs = [
            ("System Maintenance", "Scheduled maintenance completed successfully.", "low"),
            ("Backup Completed", "Daily database backup completed.", "low"),
            ("New Feature", "SMS integration is now live.", "medium")
        ]
        
        for title, msg, priority in system_msgs:
            notif = Notification(
                id=uuid4(),
                title=title,
                message=msg,
                type="system",
                reference_id=None,
                is_read=True,
                priority=priority,
                created_at=datetime.utcnow() - timedelta(days=random.randint(1, 5))
            )
            notifications.append(notif)

        if notifications:
            print(f"🚀 Inserting {len(notifications)} new notifications...")
            db.add_all(notifications)
            db.commit()
            print("✅ Notifications seeded successfully!")
        else:
            print("✨ No new notifications to add.")

    except Exception as e:
        print(f"❌ Error seeding notifications: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_notifications()

