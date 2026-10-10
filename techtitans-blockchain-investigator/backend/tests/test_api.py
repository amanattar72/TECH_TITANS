from fastapi.testclient import TestClient
from app.main import app

client=TestClient(app)
VALID="0xaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"

def test_health():
    assert client.get("/health").json()["status"]=="ok"

def test_invalid_address_rejected():
    r=client.post("/api/investigations",json={"address":"not-a-wallet","network":"ethereum","mode":"demo"})
    assert r.status_code==422

def test_demo_investigation_is_labelled():
    r=client.post("/api/investigations",json={"address":VALID,"network":"ethereum","mode":"demo"})
    assert r.status_code==200
    data=r.json(); assert data["data_mode"]=="synthetic_demo_data"
    assert data["transaction_count"]>0 and data["nodes"] and data["edges"]
    assert "synthetic" in " ".join(data["limitations"]).lower()

def test_case_create_and_update():
    r=client.post("/api/cases",json={"title":"Test case","wallet_address":VALID,"priority":"high"})
    assert r.status_code==200
    cid=r.json()["case_id"]
    u=client.patch(f"/api/cases/{cid}",json={"status":"in_review"})
    assert u.status_code==200 and u.json()["status"]=="in_review"
