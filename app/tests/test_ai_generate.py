from unittest.mock import patch

from app.schemas.ai import GeneratedTask, GeneratedTaskList
from app.services.ai_service import AIGenerationError


def test_generate_success(client, auth_headers):
    fake_result = GeneratedTaskList(
        tasks=[GeneratedTask(title="Call dentist", priority="medium")]
    )
    with patch("app.routers.ai.generate_tasks_from_text", return_value=fake_result):
        res = client.post(
            "/tasks/generate", json={"text": "Call the dentist"}, headers=auth_headers
        )
    assert res.status_code == 200
    assert res.json()[0]["title"] == "Call dentist"


def test_generate_empty_extraction(client, auth_headers):
    with patch(
        "app.routers.ai.generate_tasks_from_text",
        return_value=GeneratedTaskList(tasks=[]),
    ):
        res = client.post("/tasks/generate", json={"text": "hello"}, headers=auth_headers)
    assert res.status_code == 200
    assert res.json() == []


def test_generate_malformed_response_rejected(client, auth_headers):
    with patch(
        "app.routers.ai.generate_tasks_from_text",
        side_effect=AIGenerationError("bad json"),
    ):
        res = client.post("/tasks/generate", json={"text": "do stuff"}, headers=auth_headers)
    assert res.status_code == 422


def test_generate_empty_input_rejected(client, auth_headers):
    res = client.post("/tasks/generate", json={"text": "  "}, headers=auth_headers)
    assert res.status_code == 422