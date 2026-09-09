def test_agent_run_exposes_dry_run_and_audit(api_client):
    response = api_client.post("/agent/run", json={"request": "backup"})

    assert response.status_code == 200
    body = response.json()
    assert body["decision"]["status"] == "pending_approval"
    assert body["decision"]["action"]["dry_run"] is True
    assert body["verification"]["status"] == "skipped"

    correlation_id = body["decision"]["correlation_id"]
    audit_response = api_client.get(f"/agent/audit/{correlation_id}")

    assert audit_response.status_code == 200
    assert [event["phase"] for event in audit_response.json()["events"]] == [
        "observe",
        "decide",
        "act",
        "verify",
    ]

    approval_response = api_client.post(f"/agent/approve/{correlation_id}")
    assert approval_response.status_code == 200
    approval_body = approval_response.json()
    assert approval_body["correlation_id"] == correlation_id
    assert approval_body["status"] == "completed"
    assert approval_body["executed"] is True
    assert approval_body["backup_path"].endswith(".db")
    assert api_client.post(f"/agent/approve/{correlation_id}").status_code == 409
