"""
CleanInbox AI — API Integration Test Script
Test toan bo endpoints: Auth -> BFS -> Ethical UX -> ESG
"""
import httpx
import json
import sys

BASE = "http://127.0.0.1:8000"

def divider(title):
    print(f"\n{'='*50}")
    print(f"  {title}")
    print(f"{'='*50}")

def test_health():
    divider("1. HEALTH CHECK")
    r = httpx.get(f"{BASE}/health")
    print(f"  Status: {r.status_code}")
    print(f"  Response: {json.dumps(r.json(), indent=2)}")
    assert r.status_code == 200
    print("  >> PASSED")

def test_auth():
    divider("2. AUTH - Login (OAuth2 Password Flow)")
    r = httpx.post(f"{BASE}/api/v1/auth/token", data={
        "username": "admin@cleaninbox.ai",
        "password": "demo1234"
    })
    print(f"  Status: {r.status_code}")
    data = r.json()
    print(f"  Token: {data.get('access_token', 'N/A')[:50]}...")
    print(f"  Type: {data.get('token_type')}")
    print(f"  Expires in: {data.get('expires_in')}s")
    assert r.status_code == 200
    print("  >> PASSED")
    return data["access_token"]

def test_auth_bad():
    divider("2b. AUTH - Bad Credentials")
    r = httpx.post(f"{BASE}/api/v1/auth/token", data={
        "username": "wrong@email.com",
        "password": "wrong"
    })
    print(f"  Status: {r.status_code} (expected 401)")
    assert r.status_code == 401
    print("  >> PASSED")

def test_bfs(token):
    divider("3. FATIGUE INTELLIGENCE - Calculate BFS")
    headers = {"Authorization": f"Bearer {token}"}

    # Test contact voi BFS thap (khach hang tot)
    r = httpx.post(f"{BASE}/api/v1/fatigue/calculate", json={
        "contact_id": "test_001",
        "time_spent_seconds": 90,
        "consecutive_unread_deletes": 0,
        "received_frequency_per_week": 1.0,
        "last_open_days_ago": 2
    }, headers=headers)
    data = r.json()
    print(f"  Contact 001 (healthy):")
    print(f"    BFS: {data['bfs_score']}/100 | Risk: {data['risk_level']}")
    print(f"    Flag: {data['ethical_ux_flag']} | Action: {data['recommended_action']}")
    assert data["ethical_ux_flag"] == False
    print("  >> PASSED")

    # Test contact voi BFS cao (CRITICAL)
    r = httpx.post(f"{BASE}/api/v1/fatigue/calculate", json={
        "contact_id": "test_critical",
        "time_spent_seconds": 2,
        "consecutive_unread_deletes": 15,
        "received_frequency_per_week": 7.0,
        "last_open_days_ago": 60
    }, headers=headers)
    data = r.json()
    print(f"\n  Contact CRITICAL (fatigued):")
    print(f"    BFS: {data['bfs_score']}/100 | Risk: {data['risk_level']}")
    print(f"    Flag: {data['ethical_ux_flag']} | Action: {data['recommended_action']}")
    print(f"    Explanation: {data['explanation']}")
    assert data["ethical_ux_flag"] == True
    assert data["risk_level"] == "critical"
    print("  >> PASSED")

def test_batch_bfs(token):
    divider("4. FATIGUE INTELLIGENCE - Batch Calculate")
    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.post(f"{BASE}/api/v1/fatigue/batch-calculate", json=[
        {"contact_id": "batch_1", "time_spent_seconds": 100, "consecutive_unread_deletes": 0, "received_frequency_per_week": 1},
        {"contact_id": "batch_2", "time_spent_seconds": 10, "consecutive_unread_deletes": 6, "received_frequency_per_week": 5},
        {"contact_id": "batch_3", "time_spent_seconds": 1, "consecutive_unread_deletes": 20, "received_frequency_per_week": 7},
    ], headers=headers)
    data = r.json()
    print(f"  Total processed: {data['total_processed']}")
    print(f"  Critical count: {data['critical_count']}")
    print(f"  Critical IDs: {data['critical_contact_ids']}")
    for r in data["results"]:
        print(f"    {r['contact_id']}: BFS={r['bfs_score']} ({r['risk']})")
    assert data["total_processed"] == 3
    print("  >> PASSED")

def test_ethical_ux(token):
    divider("5. ETHICAL UX - Snooze")
    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.post(f"{BASE}/api/v1/ethical-ux/snooze", json={
        "contact_id": "test_critical",
        "snooze_days": 60
    }, headers=headers)
    data = r.json()
    print(f"  Action: {data['action']}")
    print(f"  Message: {data['message']}")
    print(f"  Snooze until: {data['snooze_until']}")
    assert data["action"] == "snoozed"
    print("  >> PASSED")

    divider("5b. ETHICAL UX - Unsubscribe")
    r = httpx.post(f"{BASE}/api/v1/ethical-ux/unsubscribe", json={
        "contact_id": "test_unsub",
        "reason": "irrelevant"
    }, headers=headers)
    data = r.json()
    print(f"  Action: {data['action']}")
    print(f"  Message: {data['message']}")
    assert data["action"] == "unsubscribed"
    print("  >> PASSED")

def test_esg(token):
    divider("6. ESG REPORTER - Summary")
    headers = {"Authorization": f"Bearer {token}"}
    r = httpx.get(f"{BASE}/api/v1/esg/summary", headers=headers)
    data = r.json()
    o = data["overall"]
    print(f"  Emails filtered: {o['emails_filtered']:,}")
    print(f"  CO2 saved: {o['co2_saved_kg']} kg ({o['co2_unit']})")
    print(f"  Cost saved: ${o['cost_saved_usd']:,.2f}")
    print(f"  Progress: {o['progress_pct']}%")
    print(f"  Monthly data points: {len(data['monthly'])}")
    assert o["emails_filtered"] > 0
    print("  >> PASSED")

    divider("6b. ESG REPORTER - Export")
    r = httpx.get(f"{BASE}/api/v1/esg/export", headers=headers)
    data = r.json()
    print(f"  Report: {data['report_name']}")
    print(f"  Standard: {data['standard']}")
    print(f"  Compliance: {data['compliance']}")
    print(f"  CO2 saved: {data['metrics']['co2_saved_ton']} ton")
    print("  >> PASSED")

def test_swagger():
    divider("7. SWAGGER DOCS")
    r = httpx.get(f"{BASE}/docs")
    print(f"  Status: {r.status_code}")
    assert r.status_code == 200
    print("  Swagger UI available at: http://localhost:8000/docs")
    print("  >> PASSED")

if __name__ == "__main__":
    print("\n" + "#"*50)
    print("  CleanInbox AI - Full API Test Suite")
    print("#"*50)

    try:
        test_health()
        token = test_auth()
        test_auth_bad()
        test_bfs(token)
        test_batch_bfs(token)
        test_ethical_ux(token)
        test_esg(token)
        test_swagger()

        print("\n" + "="*50)
        print("  ALL 9 TESTS PASSED!")
        print("="*50 + "\n")
    except Exception as e:
        print(f"\n  FAILED: {e}")
        sys.exit(1)
