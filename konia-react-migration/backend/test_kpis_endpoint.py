from fastapi.testclient import TestClient
from app.main import app

from app.api.dashboard import get_current_user_and_company

def mock_get_current_user():
    return {"company_id": 2, "email": "test@test.com"}

app.dependency_overrides[get_current_user_and_company] = mock_get_current_user
client = TestClient(app)

response = client.get("/api/kpis/resumen?periodo=2026-02")
print("Response STATUS:", response.status_code)

try:
    import json
    data = response.json()
    print("FINAL JSON:")
    print(json.dumps(data, indent=2)[:1000])
except Exception as e:
    print("Error parsing json:", e)
    print("Response text:", response.text)
