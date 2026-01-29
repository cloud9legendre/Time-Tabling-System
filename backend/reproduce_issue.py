from passlib.context import CryptContext
import sys
import hashlib

# MOCKING THE APP LOGIC
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    # 1. Try checking the SHA256 pre-hashed version (New System)
    sha256_password = hashlib.sha256(plain_password.encode()).hexdigest()
    if pwd_context.verify(sha256_password, hashed_password):
        print("   -> Match via SHA256 (New System)")
        return True
        
    # 2. Fallback: Check raw password (Legacy System)
    if len(plain_password.encode()) <= 72:
        if pwd_context.verify(plain_password, hashed_password):
            print("   -> Match via Raw (Legacy System)")
            return True
        
    return False

def get_password_hash(password):
    sha256_password = hashlib.sha256(password.encode()).hexdigest()
    return pwd_context.hash(sha256_password)

# TEST SUITE
def run_tests():
    print("--- TEST 1: New Short Password ---")
    pw = "password123"
    hashed = get_password_hash(pw)
    if verify_password(pw, hashed):
        print("✅ Success")
    else:
        print("❌ Failed")
        return False

    print("\n--- TEST 2: New Long Password (80 chars) ---")
    pw = "a" * 80
    hashed = get_password_hash(pw)
    if verify_password(pw, hashed):
        print("✅ Success")
    else:
        print("❌ Failed")
        return False

    print("\n--- TEST 3: Legacy Short Password (Backward Compatibility) ---")
    pw = "old_password"
    # Manually create a raw bcrypt hash (simulating old DB record)
    legacy_hash = pwd_context.hash(pw) 
    if verify_password(pw, legacy_hash):
        print("✅ Success")
    else:
        print("❌ Failed")
        return False

    return True

if __name__ == "__main__":
    try:
        if run_tests():
            print("\n✅ ALL TESTS PASSED")
            sys.exit(0)
        else:
            print("\n❌ SOME TESTS FAILED")
            sys.exit(1)
    except Exception as e:
        print(f"\n❌ CRASHED: {e}")
        sys.exit(1)
