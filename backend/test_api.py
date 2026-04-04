import sys
sys.path.append(".")
import logging
from fastapi.testclient import TestClient
from app.main import app
from app.db.session import SessionLocal
from app.models.verification import PasswordResetOTP

# enable logging to catch background task errors
logging.basicConfig(level=logging.DEBUG)

db = SessionLocal()
# First clear existing OTPs to prevent 429
db.query(PasswordResetOTP).delete()
db.commit()

client = TestClient(app)
email_to_test = "rsutharganpat2004@gmail.com"

print(f"Triggering forgot password for {email_to_test}...")
try:
    response = client.post("/forgotpassword", json={"email": email_to_test})
    print(f"Status: {response.status_code}")
    print(f"Body: {response.json()}")
    
    # Verify DB entry
    db.expire_all() # force refresh
    otp_entry = db.query(PasswordResetOTP).filter(PasswordResetOTP.email == email_to_test).first()
    if otp_entry:
        print(f"SUCCESS: OTP successfully written to database: {otp_entry.code}")
    else:
        print("FAIL: No OTP entry written to database!")
        
except Exception as e:
    print(f"A hidden exception occurred! {e}")
