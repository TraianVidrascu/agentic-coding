def test_project_and_entry_flow(client):
    p = client.post("/api/projects", json={"name": "Learning"}).json()

    r = client.post("/api/entries", json={
        "date": "2026-11-20", "start_time": "09:00", "end_time": "10:30",
        "project_id": p["id"], "description": "Read docs",
    })
    assert r.status_code == 201
    entry = r.json()
    assert entry["minutes"] == 90

    s = client.get("/api/summary", params={"from": "2026-11-16", "to": "2026-11-22"}).json()
    assert s["total_minutes"] == 90
    assert s["by_project"] == {"Learning": 90}

    assert client.delete(f"/api/entries/{entry['id']}").status_code == 204
    assert client.get("/api/entries").json() == []


def test_end_before_start_is_rejected(client):
    r = client.post("/api/entries", json={
        "date": "2026-11-20", "start_time": "11:00", "end_time": "10:00",
    })
    assert r.status_code == 422


def test_duplicate_project_name_conflicts(client):
    client.post("/api/projects", json={"name": "A"})
    assert client.post("/api/projects", json={"name": "A"}).status_code == 409


def test_unknown_project_id_rejected(client):
    r = client.post("/api/entries", json={
        "date": "2026-11-20", "start_time": "09:00", "end_time": "10:00", "project_id": 999,
    })
    assert r.status_code == 400
