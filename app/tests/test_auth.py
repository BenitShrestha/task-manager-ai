def test_register_success(client):
    res = client.post("/auth/register", json={"email": "a@example.com", "password": "pass1234"})
    assert res.status_code == 201
    assert res.json()["email"] == "a@example.com"
    assert "hashed_password" not in res.json()


def test_register_duplicate_email(client):
    client.post("/auth/register", json={"email": "a@example.com", "password": "pass1234"})
    res = client.post("/auth/register", json={"email": "a@example.com", "password": "other123"})
    assert res.status_code == 400


def test_login_success(client):
    client.post("/auth/register", json={"email": "a@example.com", "password": "pass1234"})
    res = client.post("/auth/login", data={"username": "a@example.com", "password": "pass1234"})
    assert res.status_code == 200
    assert "access_token" in res.json()


def test_login_wrong_password(client):
    client.post("/auth/register", json={"email": "a@example.com", "password": "pass1234"})
    res = client.post("/auth/login", data={"username": "a@example.com", "password": "wrong"})
    assert res.status_code == 401