"""Unit-тесты для UGC-сервиса (Flask)"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import pytest

from ugc_service.app import app
from ugc_service.models import init_db


@pytest.fixture
def client():
    """Фикстура для тестового клиента Flask"""
    app.config["TESTING"] = True
    app.config["DJANGO_API_URL"] = "http://localhost:8000"
    with app.test_client() as client:
        init_db()
        yield client


def test_create_review_success(client):
    """Тест: успешное создание отзыва"""
    response = client.post(
        "/ugc/reviews/",
        json={
            "product_id": 1,
            "user_id": "user",
            "rating": 5,
            "comment": "Комментарий",
        },
    )
    assert response.status_code in [201, 404]


def test_create_review_invalid_rating(client):
    """Тест: рейтинг больше 5"""
    response = client.post(
        "/ugc/reviews/",
        json={
            "product_id": 1,
            "user_id": "user",
            "rating": 10,
            "comment": "Комментарий",
        },
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert data["error"]["code"] == "VALIDATION_ERROR"


def test_create_review_empty_comment(client):
    """Тест: пустой комментарий"""
    response = client.post(
        "/ugc/reviews/",
        json={"product_id": 1, "user_id": "test_user", "rating": 5, "comment": ""},
    )
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False


def test_get_reviews(client):
    """Тест: получение списка отзывов"""
    client.post(
        "/ugc/reviews/",
        json={
            "product_id": 1,
            "user_id": "test_user",
            "rating": 5,
            "comment": "Тестовый отзыв",
        },
    )

    response = client.get("/ugc/reviews/?product_id=1")
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)


def test_update_review_status(client):
    """Тест: обновление статуса отзыва"""
    create_resp = client.post(
        "/ugc/reviews/",
        json={"product_id": 1, "user_id": "admin", "rating": 5, "comment": "comment"},
    )

    review_id = create_resp.get_json()["id"]

    response = client.patch(
        f"/ugc/reviews/{review_id}/status", json={"status": "active"}
    )
    assert response.status_code == 200

    data = response.get_json()
    assert data["status"] == "active"
