def test_create_and_get_task(client, auth_headers):
    res = client.post("/tasks", json={"title": "Test task"}, headers=auth_headers)
    assert res.status_code == 201
    task_id = res.json()["id"]

    res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "Test task"


def test_list_tasks_scoped_to_user(client, auth_headers):
    client.post("/tasks", json={"title": "Task 1"}, headers=auth_headers)
    client.post("/tasks", json={"title": "Task 2"}, headers=auth_headers)
    res = client.get("/tasks", headers=auth_headers)
    assert res.status_code == 200
    assert len(res.json()) == 2


def test_update_task(client, auth_headers):
    res = client.post("/tasks", json={"title": "Old"}, headers=auth_headers)
    task_id = res.json()["id"]
    res = client.put(f"/tasks/{task_id}", json={"title": "New"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json()["title"] == "New"


def test_delete_task(client, auth_headers):
    res = client.post("/tasks", json={"title": "Delete me"}, headers=auth_headers)
    task_id = res.json()["id"]
    res = client.delete(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 204
    res = client.get(f"/tasks/{task_id}", headers=auth_headers)
    assert res.status_code == 404


def test_cannot_access_other_users_task(client, auth_headers):
    res = client.post("/tasks", json={"title": "Mine"}, headers=auth_headers)
    task_id = res.json()["id"]

    client.post("/auth/register", json={"email": "b@example.com", "password": "pass1234"})
    login = client.post("/auth/login", data={"username": "b@example.com", "password": "pass1234"})
    other_headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    res = client.get(f"/tasks/{task_id}", headers=other_headers)
    assert res.status_code == 404


def test_unauthenticated_request_rejected(client):
    res = client.get("/tasks")
    assert res.status_code == 401