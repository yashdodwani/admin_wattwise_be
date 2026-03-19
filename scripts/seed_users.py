"""
Seed script to populate the users table with realistic Indian electricity consumer data,
as well as corresponding records in reference tables, complaints, transactions,
sms, admin, and settings.

Usage:
    python -m scripts.seed_users             # seed 200 users (default)
    python -m scripts.seed_users --count 500 # seed 500 users
    python -m scripts.seed_users --clear     # clear existing tables before seeding
"""

import uuid
import random
import argparse
from datetime import datetime, timedelta

from config.database import SessionLocal, engine, Base
from models.user import User
from models.complaint import Complaint, Priority, Status
from models.transaction import Transaction, PaymentMethod, TransactionStatus
from models.sms import SMSLog, SMSTemplate
from models.admin import Admin
from models.settings import BillingSettings
from models.reference_data import State, Discom

# ---------------------------------------------------------------------------
# State → DISCOM mapping
# ---------------------------------------------------------------------------
STATE_DISCOMS = {
    "Andhra Pradesh": [
        "APEPDCL", "APSPDCL", "APCPDCL",
    ],
    "Telangana": [
        "TGSPDCL", "TGNPDCL",
    ],
    "Karnataka": [
        "BESCOM", "MESCOM", "HESCOM", "GESCOM", "CESC Mysuru",
    ],
    "Tamil Nadu": [
        "TANGEDCO",
    ],
    "Kerala": [
        "KSEB",
    ],
    "Maharashtra": [
        "MSEDCL", "Tata Power", "Adani Electricity Mumbai", "BEST Undertaking",
    ],
    "Gujarat": [
        "DGVCL", "MGVCL", "PGVCL", "UGVCL", "Torrent Power",
    ],
    "Rajasthan": [
        "JVVNL", "AVVNL", "JDVVNL",
    ],
    "Uttar Pradesh": [
        "DVVNL", "MVVNL", "PVVNL", "PuVVNL", "NPCL", "KESCO",
    ],
    "Delhi": [
        "BRPL", "BYPL", "TPDDL", "NDMC",
    ],
    "Haryana": [
        "DHBVN", "UHBVN",
    ],
    "Madhya Pradesh": [
        "MP Madhya Kshetra Vidyut Vitaran Company",
        "MP Paschim Kshetra Vidyut Vitaran Company",
        "MP Poorv Kshetra Vidyut Vitaran Company",
    ],
    "Punjab": [
        "PSPCL",
    ],
    "Bihar": [
        "NBPDCL", "SBPDCL",
    ],
    "West Bengal": [
        "WBSEDCL", "CESC Limited",
    ],
    "Odisha": [
        "CESU", "NESCO", "SOUTHCO", "WESCO",
    ],
    "Chhattisgarh": [
        "CSPDCL",
    ],
    "Uttarakhand": [
        "UPCL",
    ],
    "Himachal Pradesh": [
        "HPSEBL",
    ],
}

# ---------------------------------------------------------------------------
# Sample Indian names
# ---------------------------------------------------------------------------
FIRST_NAMES = [
    "Aarav", "Aditya", "Akash", "Amit", "Ananya", "Arjun", "Aryan", "Ayesha",
    "Deepak", "Divya", "Farhan", "Fatima", "Gaurav", "Geeta", "Harish", "Isha",
    "Jatin", "Kavya", "Kiran", "Komal", "Lakshmi", "Manish", "Meera", "Mohan",
    "Neha", "Nikhil", "Nisha", "Pankaj", "Pooja", "Pradeep", "Priya", "Rahul",
    "Raj", "Rajesh", "Rakesh", "Ramesh", "Riya", "Rohit", "Sachin", "Sahil",
    "Sandeep", "Sanjay", "Sara", "Seema", "Shweta", "Sneha", "Sonia", "Sunil",
    "Suresh", "Tanvi", "Tarun", "Usha", "Vijay", "Vikram", "Vinay", "Vishal",
    "Yash", "Zara", "Abhinav", "Bhavna", "Chetan", "Dipti",
]

LAST_NAMES = [
    "Agarwal", "Ahuja", "Bansal", "Bhat", "Chandra", "Chauhan", "Chopra",
    "Das", "Desai", "Deshpande", "Dubey", "Gandhi", "Garg", "Ghosh", "Goyal",
    "Gupta", "Iyer", "Jain", "Joshi", "Kapoor", "Kaur", "Khan", "Khanna",
    "Kumar", "Lal", "Malhotra", "Mehta", "Mishra", "Nair", "Naik", "Patel",
    "Patil", "Pillai", "Rajan", "Rao", "Reddy", "Saxena", "Shah", "Sharma",
    "Shukla", "Singh", "Sinha", "Srivastava", "Tiwari", "Tripathi", "Varma",
    "Verma", "Yadav", "Pandey", "Menon",
]


# ---------------------------------------------------------------------------
# Generator helpers
# ---------------------------------------------------------------------------
def random_name() -> str:
    return f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"

def random_phone() -> str:
    return f"{random.randint(6, 9)}" + "".join(str(random.randint(0, 9)) for _ in range(9))

def random_meter_id() -> str:
    return "MTR" + "".join(str(random.randint(0, 9)) for _ in range(8))

def random_consumer_id(counter: int) -> str:
    return f"CON{counter:07d}"

def random_user_id(counter: int) -> str:
    return f"USR{counter:07d}"

def random_bill_amount() -> float:
    return round(random.uniform(200, 8000), 2)

def random_last_payment_date() -> datetime | None:
    if random.random() < 0.15:
        return None
    days_ago = random.randint(1, 90)
    return datetime.utcnow() - timedelta(days=days_ago)

def random_balance(bill: float) -> tuple[float, float]:
    """Return (remaining_balance, balance_used) that sum to bill."""
    used_pct = random.uniform(0, 1)
    balance_used = round(bill * used_pct, 2)
    remaining = round(bill - balance_used, 2)
    return remaining, balance_used

def random_state_discom() -> tuple[str, str]:
    state = random.choice(list(STATE_DISCOMS.keys()))
    discom = random.choice(STATE_DISCOMS[state])
    return state, discom

# ---------------------------------------------------------------------------
# Seeding
# ---------------------------------------------------------------------------
def seed_users(count: int = 200, clear: bool = False) -> None:
    Base.metadata.create_all(bind=engine)   # ensure tables exist

    db = SessionLocal()
    try:
        if clear:
            db.query(Complaint).delete()
            db.query(Transaction).delete()
            db.query(SMSLog).delete()
            db.query(User).delete()
            db.query(SMSTemplate).delete()
            db.query(Discom).delete()
            db.query(State).delete()
            db.query(BillingSettings).delete()
            db.query(Admin).delete()
            db.commit()
            print("🗑️  Cleared existing records across all seeded tables.")

        # Seed states and discoms
        state_objs = {}
        for state_name, discom_list in STATE_DISCOMS.items():
            state_obj = db.query(State).filter(State.name == state_name).first()
            if not state_obj:
                state_obj = State(name=state_name)
                db.add(state_obj)
                db.flush()
            state_objs[state_name] = state_obj

            for discom_name in discom_list:
                discom_obj = db.query(Discom).filter(Discom.name == discom_name, Discom.state_id == state_obj.id).first()
                if not discom_obj:
                    discom_obj = Discom(name=discom_name, state_id=state_obj.id)
                    db.add(discom_obj)

        db.commit()

        # Seed SMS Templates
        template_names = ["Payment Reminder", "Outage Alert", "Welcome Message"]
        templates = []
        for t_name in template_names:
            tpl = db.query(SMSTemplate).filter(SMSTemplate.name == t_name).first()
            if not tpl:
                tpl = SMSTemplate(
                    template_id=f"TPL_{uuid.uuid4().hex[:8].upper()}",
                    name=t_name,
                    body=f"This is a dummy body for {t_name}",
                    category=t_name.split()[0].lower()
                )
                db.add(tpl)
                db.flush()
            templates.append(tpl)
        db.commit()

        # Seed Settings and Admin
        if not db.query(BillingSettings).first():
            settings = BillingSettings(
                billing_cycle_days=30,
                late_fee_amount=50.0,
                grace_period_days=5,
                auto_disconnect_enabled=False
            )
            db.add(settings)
        
        if not db.query(Admin).first():
            admin = Admin(
                admin_id="ADM123456",
                name="System Admin",
                email="admin@wattwise.com",
                phone_number="9999999999",
                descom_name="Global",
                hashed_password="hashed_dummy_password"
            )
            db.add(admin)
        db.commit()

        # Find the highest existing numeric suffix to avoid collisions
        last_user = db.query(User).order_by(User.user_id.desc()).first()
        start_index = 1
        if last_user and type(last_user.user_id) is str and last_user.user_id.startswith("USR"):
            try:
                start_index = int(last_user.user_id[3:]) + 1
            except (ValueError, IndexError):
                pass
        else:
            # fallback if user_id format differs
            pass

        users = []
        complaints = []
        transactions = []
        sms_logs = []

        for i in range(start_index, start_index + count):
            bill = random_bill_amount()
            remaining, used = random_balance(bill)
            last_payment = random_last_payment_date()
            state, discom = random_state_discom()
            has_active_complaint = random.random() < 0.10

            user_uuid = uuid.uuid4()
            u_id = random_user_id(i)
            
            # Complaint Logic
            complaint_id_str = None
            if has_active_complaint:
                complaint_id_str = f"CMP{uuid.uuid4().hex[:8].upper()}"
                complaint = Complaint(
                    id=uuid.uuid4(),
                    complaint_id=complaint_id_str,
                    user_id=user_uuid,
                    issue_type=random.choice(["Power Outage", "Billing Issue", "Meter Fault"]),
                    priority=random.choice(list(Priority)),
                    status=random.choice([Status.OPEN, Status.IN_PROGRESS, Status.ESCALATED]),
                    agent_name=random.choice(["Alice", "Bob", "Charlie", None]),
                    description="Dummy complaint automatically generated.",
                    created_at=datetime.utcnow() - timedelta(days=random.randint(1, 10))
                )
                complaints.append(complaint)

            user = User(
                id=user_uuid,
                user_id=u_id,
                consumer_id=random_consumer_id(i),
                name=random_name(),
                meter_id=random_meter_id(),
                phone=random_phone(),
                state=state,
                discom=discom,
                bill_amount=bill,
                last_payment_date=last_payment,
                remaining_balance=remaining,
                balance_used=used,
                active_complaint=has_active_complaint,
                complaint_id=complaint_id_str,
                is_active=random.random() > 0.05,           # 95% active
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
            )
            users.append(user)
            
            # Transaction Logic
            if last_payment:
                txn = Transaction(
                    id=uuid.uuid4(),
                    transaction_id=f"TXN{uuid.uuid4().hex[:10].upper()}",
                    user_id=u_id,
                    state=state,
                    amount=round(bill * random.uniform(0.5, 1.0), 2),
                    payment_method=random.choice(["UPI", "Net Banking", "Credit Card", "Debit Card", "Wallet"]),
                    status="Success",
                    created_at=last_payment
                )
                transactions.append(txn)
                
            # SMS Log Logic
            if random.random() < 0.5: # 50% users get an SMS log
                sms = SMSLog(
                    id=uuid.uuid4(),
                    sms_id=f"SMS{uuid.uuid4().hex[:8].upper()}",
                    user_id=u_id,
                    phone_number=user.phone,
                    message=random.choice(["Payment Reminder", "Outage Alert", "Welcome to WattWise!"]),
                    status=random.choice(["Sent", "Sent", "Sent", "Failed", "Pending"]),
                    sent_at=datetime.utcnow() - timedelta(days=random.randint(0, 30))
                )
                sms_logs.append(sms)

        db.bulk_save_objects(users)
        db.bulk_save_objects(complaints)
        db.bulk_save_objects(transactions)
        db.bulk_save_objects(sms_logs)
        
        db.commit()
        print(f"✅  Seeded {count} user(s) successfully (user_id: {random_user_id(start_index)} → {random_user_id(start_index + count - 1)}).")
        print(f"✅  Seeded {len(complaints)} complaints.")
        print(f"✅  Seeded {len(transactions)} transactions.")
        print(f"✅  Seeded {len(sms_logs)} SMS logs.")

    except Exception as e:
        db.rollback()
        print(f"❌  Seeding failed: {e}")
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the users table and related tables with dummy Indian electricity consumer data.")
    parser.add_argument("--count", type=int, default=200, help="Number of users to seed (default: 200)")
    parser.add_argument("--clear", action="store_true", help="Clear existing users before seeding")
    args = parser.parse_args()

    seed_users(count=args.count, clear=args.clear)
