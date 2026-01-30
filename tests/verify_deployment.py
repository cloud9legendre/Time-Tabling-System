import urllib3
import requests
import sys
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Configuration
BASE_URL = "https://localhost"  # Updated to HTTPS
ADMIN_EMAIL = "admin@uom.lk" 
ADMIN_PASSWORD = "password123"       

# ... (rest of imports)

def print_pass(msg):
    print(f"[PASS] {msg}")

def print_fail(msg, details=""):
    print(f"[FAIL] {msg}")
    if details:
        print(f"   Details: {details}")

import re

def login():
    """Simulates login and returns a session with cookies."""
    session = requests.Session()
    session.verify = False 
    try:
        # 1. Get Login Page to get CSRF token
        response = session.get(f"{BASE_URL}/login")
        if response.status_code != 200:
             print_fail("Could not load login page", f"Status: {response.status_code}")
             return None
             
        # Extract CSRF token
        match = re.search(r'name="csrf_token" value="(.*?)"', response.text)
        if not match:
            print_fail("Could not find CSRF token on login page")
            return None
        csrf_token = match.group(1)
        
        # 2. Post Login
        login_data = {
            "email": ADMIN_EMAIL, 
            "password": ADMIN_PASSWORD,
            "csrf_token": csrf_token
        }
        response = session.post(f"{BASE_URL}/login", data=login_data)
        
        if response.status_code == 200 and "Admin Dashboard" in response.text:
            print_pass("Admin Login successful")
            
            if "Change Password" in response.text:
                print_pass("Super Admin 'Change Password' button visible")
            else:
                print_warning("Change Password button missing")
                
            return session
        else:
            print_fail("Admin Login failed", f"Status: {response.status_code}, URL: {response.url}")
            return None
    except requests.exceptions.ConnectionError:
        print_fail("Could not connect to server. Is it running?")
        return None

def verify_modules(session):
    """Verifies module list and basic CRUD flow."""
    print("\n--- Verifying Modules ---")
    
    # 1. List Modules (Dashboard)
    response = session.get(f"{BASE_URL}/?tab=resources", verify=False)
    if response.status_code == 200:
        print_pass("Loaded Resources Tab")
        if "Manage Modules" in response.text:
            print_pass("Modules section visible")
            if "<th>Dept</th>" in response.text:
                print_pass("Modules table has 'Dept' column")
            else:
                print_fail("'Dept' column missing in Modules table")
        else:
            print_fail("Modules section not found in dashboard")
    else:
        print_fail("Failed to load dashboard")

def verify_labs(session):
    """Verifies labs list."""
    print("\n--- Verifying Labs ---")
    response = session.get(f"{BASE_URL}/", verify=False)
    if "Manage Labs" in response.text:
         print_pass("Labs section visible")
    else:
         print_fail("Labs section missing")

def verify_leaves(session):
    """Verifies leaves tab and new admin form."""
    print("\n--- Verifying Leaves ---")
    response = session.get(f"{BASE_URL}/", verify=False)
    if "Place Leave (Admin Override)" in response.text:
         print_pass("Admin Leave form visible")
    else:
         print_fail("Admin Leave form missing")
    if "Multi-day" in response.text:
         print_pass("Multi-day toggle visible")
    else:
         print_fail("Multi-day toggle missing")

    # Verify AJAX/Toast linkage
    if "ajax_handler.js" in response.text and "toast.js" in response.text:
         print_pass("AJAX & Toast scripts linked")
    else:
         print_fail("AJAX/Toast scripts missing")

    if 'class="container"' in response.text or "class='container'" in response.text:
         print_pass("Main Container present for AJAX")
    else:
         print_fail("Main Container missing (AJAX will reload)")
         
    if 'name="repeat_until"' in response.text:
         print_pass("Recurring Field 'repeat_until' corrected")
    else:
         print_fail("Recurring Field mismatch (still repeat_until_date?)")

def run_smoke_tests():
    print("Starting Smoke Tests for Lab Timetabling System...")
    
    session = login()
    if not session:
        sys.exit(1)
        
    verify_modules(session)
    verify_labs(session)
    verify_leaves(session)
    
    print("\nVerification Complete.")

if __name__ == "__main__":
    run_smoke_tests()
