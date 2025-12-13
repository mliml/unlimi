"""
Database Initialization Script

Creates essential data after migrations:
- Default therapist (id='01')
- Universal invitation code
"""
import os
import sys
from sqlalchemy.orm import Session

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.database import SessionLocal
from app.models.therapist import Therapist
from app.models.invitation_code import InvitationCode


def init_therapists(db: Session):
    """Initialize default therapist."""
    print("🔍 Checking therapists...")

    therapist = db.query(Therapist).filter(Therapist.id == '01').first()
    if therapist:
        print("✅ Default therapist already exists")
        return

    print("📝 Creating default therapist...")
    default_therapist = Therapist(
        id='01',
        name='默认心理咨询师',
        age=35,
        info='经验丰富的专业心理咨询师，专注于情绪管理和心理健康。',
        prompt='你是一位专业的心理咨询师，请以温和、理解和支持的态度与来访者交流。'
    )
    db.add(default_therapist)
    db.commit()
    print("✅ Default therapist created (id='01')")


def init_invitation_codes(db: Session):
    """Initialize universal invitation code."""
    print("🔍 Checking invitation codes...")

    universal_code = 'WuSY_940315'
    invitation = db.query(InvitationCode).filter(InvitationCode.code == universal_code).first()

    if invitation:
        print(f"✅ Universal invitation code already exists: {universal_code}")
        return

    print(f"📝 Creating universal invitation code: {universal_code}")
    invitation = InvitationCode(
        code=universal_code,
        is_universal=True,
        is_used=False
    )
    db.add(invitation)
    db.commit()
    print(f"✅ Universal invitation code created: {universal_code}")


def main():
    """Initialize all essential data."""
    print("=" * 60)
    print("Database Initialization")
    print("=" * 60)
    print()

    db = SessionLocal()
    try:
        init_therapists(db)
        print()
        init_invitation_codes(db)
        print()
        print("=" * 60)
        print("✅ Database initialization complete!")
        print("=" * 60)
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        db.rollback()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
