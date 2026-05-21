"""Простые тесты для FastAPI сервиса"""

import pytest
from httpx import ASGITransport, AsyncClient

from notification_service.main import app


@pytest.mark.asyncio
async def test_health_check():
    """Тест: проверка здоровья сервиса"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["service"] == "notification_service"


@pytest.mark.asyncio
async def test_verify_token_invalid():
    """Тест: проверка невалидного токена"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/auth/verify", json={"token": "invalid-token"})
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False


@pytest.mark.asyncio
async def test_verify_token_empty():
    """Тест: проверка пустого токена"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.post("/auth/verify", json={})
        assert response.status_code == 400


@pytest.mark.asyncio
async def test_protected_endpoint_without_token():
    """Тест: защищённый эндпоинт без токена"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/auth/me")
        assert response.status_code == 401


@pytest.mark.asyncio
async def test_reports_orders_without_token():
    """Тест: отчёт без токена"""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        response = await client.get("/reports/orders")
        assert response.status_code == 401
