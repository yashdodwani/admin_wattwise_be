"""
Seed script to populate the users table with realistic Indian electricity consumer data.
Covers all major states and DISCOMs.

Usage:
    python -m scripts.seed_users             # seed 200 users (default)
    python -m scripts.seed_users --count 500 # seed 500 users
    python -m scripts.seed_users --clear     # clear existing users before seeding
"""

import uuid
import random
import argparse
from datetime import datetime, timedelta
from config.database import SessionLocal, engine, Base
from models.user import User  # noqa: F401 — registers table on Base

# ---------------------------------------------------------------------------
# State → DISCOM mapping
# ---------------------------------------------------------------------------
STATE_DISCOMS = {
    "Andhra Pradesh": [
        "APEPDCL",
        "APSPDCL",
        "APCPDCL",
    ],
    "Telangana": [
        "TGSPDCL",
        "TGNPDCL",
    ],
    "Karnataka": [
        "BESCOM",
        "MESCOM",
        "HESCOM",
        "GESCOM",
        "CESC Mysuru",
    ],
    "Tamil Nadu": [
        "TANGEDCO",
    ],
    "Kerala": [
        "KSEB",
    ],
    "Maharashtra": [
        "MSEDCL",
        "Tata Power",
        "Adani Electricity Mumbai",
        "BEST Undertaking",
    ],
    "Gujarat": [
        "DGVCL",
        "MGVCL",
        "PGVCL",
        "UGVCL",
        "Torrent Power",
    ],
    "Rajasthan": [
        "JVVNL",
        "AVVNL",
        "JDVVNL",
    ],
    "Uttar Pradesh": [
        "DVVNL",
        "MVVNL",
        "PVVNL",
        "PuVVNL",
        "NPCL",
        "KESCO",
    ],
    "Delhi": [
        "BRPL",
        "BYPL",
        "TPDDL",
        "NDMC",
    ],
    "Haryana": [
        "DHBVN",
        "UHBVN",
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
        "NBPDCL",
        "SBPDCL",
    ],
    "West Bengal": [
        "WBSEDCL",
        "CESC Limited",
    ],
    "Odisha": [
        "CESU",
        "NESCO",
        "SOUTHCO",
        "WESCO",
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
    # Indian mobile numbers: 10 digits starting with 6-9
    return f"{random.randint(6, 9)}" + "".join(str(random.randint(0, 9)) for _ in range(9))


def random_meter_id() -> str:
    return "MTR" + "".join(str(random.randint(0, 9)) for _ in range(8))


def random_consumer_id(counter: int) -> str:
    return f"CON{counter:07d}"


def random_user_id(counter: int) -> str:
    return f"USR{counter:07d}"


def random_bill_amount() -> float:
    # Typical Indian electricity bill: ₹200 – ₹8000
    return round(random.uniform(200, 8000), 2)


def random_last_payment_date() -> datetime | None:
    if random.random() < 0.15:   # 15% never paid
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
            deleted = db.query(User).delete()
            db.commit()
            print(f"🗑️  Cleared {deleted} existing user(s).")

        # Find the highest existing numeric suffix to avoid collisions
        last_user = db.query(User).order_by(User.user_id.desc()).first()
        start_index = 1
        if last_user:
            try:
                start_index = int(last_user.user_id[3:]) + 1
            except (ValueError, IndexError):
                pass

        users = []
        for i in range(start_index, start_index + count):
            bill = random_bill_amount()
            remaining, used = random_balance(bill)
            last_payment = random_last_payment_date()
            state, discom = random_state_discom()

            user = User(
                id=uuid.uuid4(),
                user_id=random_user_id(i),
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
                active_complaint=random.random() < 0.10,   # 10% have active complaint
                complaint_id=None,
                is_active=random.random() > 0.05,           # 95% active
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 365)),
            )
            users.append(user)

        db.bulk_save_objects(users)
        db.commit()
        print(f"✅  Seeded {count} user(s) successfully (user_id: {random_user_id(start_index)} → {random_user_id(start_index + count - 1)}).")

    except Exception as e:
        db.rollback()
        print(f"❌  Seeding failed: {e}")
        raise
    finally:
        db.close()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Seed the users table with dummy Indian electricity consumer data.")
    parser.add_argument("--count", type=int, default=200, help="Number of users to seed (default: 200)")
    parser.add_argument("--clear", action="store_true", help="Clear existing users before seeding")
    args = parser.parse_args()

    seed_users(count=args.count, clear=args.clear)

