# Интернет магазин (1 спринт)

Backend-приложение для интернет-магазина на Django

## Сущности

- **Product** — товар
- **Category** — категория товара
- **Cart** — корзина
- **Order** — заказ
- **OrderItem** — позиции заказа

## Установка и запуск

### 1. Клонировать репозиторий
```bash
git clone <url>
cd sem2_python_web
```

### 2. Создать виртуальное окружение
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
# .venv\Scripts\activate   # Windows
```

### 3. Установить зависимости
```bash
uv add django djangorestframework psycopg2-binary
```

### 4. Настроить PostgreSQL

Создать базу данных:
```sql
CREATE DATABASE shop_db;
CREATE USER shop_user WITH PASSWORD 'python';
GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;
ALTER SCHEMA public OWNER TO shop_user;
```

В `src/config/settings.py` проверить настройки БД:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'shop_db',
        'USER': 'shop_user',
        'PASSWORD': 'python',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Применить миграции
```bash
cd src
python manage.py migrate
python manage.py createsuperuser
```

### 6. Запустить сервер
```bash
python manage.py runserver
```

## API Эндпоинты

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/products/` | Список товаров (пагинация) |
| GET | `/api/products/?category=1` | Фильтр по категории |
| GET | `/api/products/{id}/` | Детали товара |
| GET | `/api/categories/` | Список категорий |
| POST | `/api/cart/` | Добавить товар в корзину |
| GET | `/api/cart/?session_key=xxx` | Просмотр корзины |
| POST | `/api/orders/` | Оформить заказ |
| GET | `/api/orders/?session_key=xxx` | История заказов |

## Примеры запросов

### Добавить товар в корзину
```bash
curl -X POST http://127.0.0.1:8000/api/cart/ \
  -H "Content-Type: application/json" \
  -d '{"session_key": "test123", "product": 1, "quantity": 2}'
```

### Оформить заказ
```bash
curl -X POST http://127.0.0.1:8000/api/orders/ \
  -H "Content-Type: application/json" \
  -d '{"session_key": "test123", "user_email": "test@example.com"}'
```

## Админка

- URL: `http://127.0.0.1:8000/admin/`
- Логин/пароль: создаются через `createsuperuser`
