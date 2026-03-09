"""
Quick test: call the backend API and show what fields come back for the first registro.
Uses the same JWT approach as the frontend.
"""
import requests, json

# First, login to get token
base = "http://localhost:8000"

# Try to get a token - use same credentials as the app
login_resp = requests.post(f"{base}/api/auth/login", json={"username": "admin", "password": "admin"}, timeout=10)
print("Login status:", login_resp.status_code)
if login_resp.status_code != 200:
    print("Login response:", login_resp.text[:300])
    # Try with cookies approach
    token = None
else:
    token = login_resp.json().get("access_token")

if token:
    headers = {"Authorization": f"Bearer {token}"}
    resp = requests.get(
        f"{base}/api/dashboard/detalle-uuid?periodo=2026-02&page=1&limit=3",
        headers=headers, timeout=15
    )
    print("Detalle UUID status:", resp.status_code)
    if resp.status_code == 200:
        data = resp.json()
        print("Total:", data.get("total"))
        print("First registro keys:", list(data.get("registros", [{}])[0].keys()) if data.get("registros") else "None")
        for r in data.get("registros", [])[:3]:
            print(json.dumps({
                "uuid": r.get("uuid", "")[:12],
                "nombre_emisor": r.get("nombre_emisor"),
                "rfc_emisor": r.get("rfc_emisor"),
                "nombre_receptor": r.get("nombre_receptor"),
                "rfc_receptor": r.get("rfc_receptor"),
            }, ensure_ascii=False))
    else:
        print("Error:", resp.text[:300])
