"""
Quick script to clear stale password reset OTP records from the database.
Run this if you're getting 429 errors and need to reset the OTP state.
"""

from app.db.session import SessionLocal
from app.models.verification import PasswordResetOTP
from datetime import datetime

def clear_stale_otps(email: str = None):
    """
    Clear stale OTP records from the database.
    
    Args:
        email: If provided, only clear OTPs for this email. 
               If None, clear all expired OTPs.
    """
    db = SessionLocal()
    try:
        if email:
            # Clear all OTPs for specific email
            count = db.query(PasswordResetOTP).filter(
                PasswordResetOTP.email == email
            ).delete()
            print(f"✅ Cleared {count} OTP record(s) for {email}")
        else:
            # Clear all expired OTPs
            now = datetime.utcnow()
            count = db.query(PasswordResetOTP).filter(
                PasswordResetOTP.expires_at < now
            ).delete()
            print(f"✅ Cleared {count} expired OTP record(s)")
        
        db.commit()
        print("✨ Database cleanup complete!")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
        print(f"Clearing OTP records for: {email}")
        clear_stale_otps(email)
    else:
        print("Clearing all expired OTP records...")
        clear_stale_otps()
