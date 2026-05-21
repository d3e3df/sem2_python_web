# Спринт 4 — FastAPI сервис

## Цель спринта

Добавить современный FastAPI сервис с асинхронностью, JWT авторизацией, фоновыми задачами и интеграцией с существующими Django и Flask сервисами.

---

## Что сделано

### FastAPI сервис (порт 8001)

- **JWT авторизация**: регистрация, логин, защищённые эндпоинты
- **PostgreSQL**: хранение пользователей (таблица `users`)
- **Асинхронные эндпоинты**: `async/await` для всех операций
- **Фоновые задачи**: отправка уведомлений через `BackgroundTasks`
- **Отчёты**: реальные данные из Django API
- **OpenAPI документация**: автоматическая на `/docs`

### Интеграция

- **Flask -> FastAPI**: при создании отзыва отправляется уведомление (с сервис-токеном)
- **FastAPI -> Django**: отчёт по заказам получает реальные данные из Django API
- **Единый формат ошибок**: все сервисы возвращают `{"success": false, "error": {...}}`

---

## Структура

```
notification_service/
├── __init__.py
├── main.py           # FastAPI приложение
├── auth.py           # JWT, хеширование паролей
└── schemas.py        # Pydantic схемы
```

---

## Запуск

### 1. Запустить Django (порт 8000)

```bash
cd ~/PycharmProjects/sem2_python_web/src
python manage.py runserver
```

### 2. Запустить Flask (порт 5001)

```bash
cd ~/PycharmProjects/sem2_python_web
export FLASK_APP=ugc_service.app
flask run --port=5001
```

### 3. Запустить FastAPI (порт 8001)

```bash
cd ~/PycharmProjects/sem2_python_web
uvicorn notification_service.main:app --reload --port 8001
```

---

## API Эндпоинты

| Метод | Эндпоинт | Описание | Авторизация    |
|-------|----------|----------|----------------|
| GET | `/health` | Проверка здоровья | -              |
| POST | `/auth/register` | Регистрация | -              |
| POST | `/auth/login` | Логин → JWT токен | -              |
| GET | `/auth/me` | Информация о пользователе | + JWT          |
| POST | `/notify` | Отправка уведомления (фоновая задача) | + Сервис-токен |
| GET | `/reports/orders` | Отчёт по заказам | + JWT          |
| POST | `/auth/verify` | Проверка JWT токена | -              |

---

## Примеры запросов

### 1. Регистрация

```bash
curl -X POST http://127.0.0.1:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "email": "example.mail.ru", "password": "qwerty"}'
```

### 2. Логин

```bash
curl -X POST http://127.0.0.1:8001/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "qwerty"}'
```

Ответ: `{"access_token": "...", "token_type": "bearer"}`

### 3. Защищённый эндпоинт

```bash
TOKEN="..."
curl -X GET http://127.0.0.1:8001/auth/me \
  -H "Authorization: Bearer $TOKEN"
```

### 4. Отчёт по заказам

```bash
curl -X GET "http://127.0.0.1:8001/reports/orders?days=7" \
  -H "Authorization: Bearer $TOKEN"
```

### 5. Уведомление (сервис-токен)

```bash
curl -X POST http://127.0.0.1:8001/notify \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer internal-service-token" \
  -d '{"user_id": "user", "message": "Тест"}'
```