import requests

BASE_URL = "http://localhost:8000"

def test_api():
    # Login
    resp = requests.post(f"{BASE_URL}/api/auth/login", data={
        "username": "2",  # Replace with valid if needed, usually just 'admin@example.com' or 'test' depending on DB
        "password": "password"
    })
    
    if resp.status_code != 200:
        print("Login failed, using fallback mock token if allowed or please check DB users.")
        # Alternatively, let's just bypass auth by writing a temporary unprotected test endpoint in dashboard.py
        
test_api()
