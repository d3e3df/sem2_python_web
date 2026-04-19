# Интернет-магазин. Спринт 2

## **Цель спринта**

Отделить бизнес-логику от HTTP-слоя, ввести сервисный слой и подготовить кодовую базу к расширению.

---

## **Что сделано**

| Компонент | Описание |
|-----------|----------|
| **Domain Layer** | Доменные исключения (ProductNotFoundError, NotEnoughStockError, CartEmptyError, OrderNotFoundError) |
| **Services Layer** | Бизнес-логика вынесена в `services/` (cart_service, order_service, product_service) |
| **API Layer** | `api/views.py`, `api/serializers.py`, `api/urls.py` — только HTTP-слой |
| **Unit-тесты** | 20 тестов на сервисы (без HTTP, SQLite в памяти) |
| **Единый формат ошибок** | `{"success": false, "error": {"code": "...", "message": ...}}` |


## **Запуск проекта**

### 1. Установка зависимостей

```bash
uv add django djangorestframework psycopg2-binary
```

### 2. Настройка PostgreSQL

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE shop_db;
CREATE USER shop_user WITH PASSWORD 'shop123';
GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;
ALTER SCHEMA public OWNER TO shop_user;
\q
```

### 3. Применить миграции

```bash
cd src
python manage.py migrate
python manage.py createsuperuser
```

### 4. Запустить сервер

```bash
python manage.py runserver
```

## **Запуск тестов**

```bash
python manage.py test tests/ --settings=tests.test_settings
```

## **API Эндпоинты**

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/products/` | Список товаров (пагинация) |
| GET | `/api/products/?category=1` | Фильтр по категории |
| GET | `/api/products/{id}/` | Детали товара |
| GET | `/api/categories/` | Список категорий |
| POST | `/api/cart/` | Добавить товар в корзину |
| GET | `/api/cart/?session_key=xxx` | Просмотр корзины |
| DELETE | `/api/cart/clear/?session_key=xxx` | Очистить корзину |
| POST | `/api/orders/` | Оформить заказ |
| GET | `/api/orders/?session_key=xxx` | История заказов |
| GET | `/api/orders/{id}/?session_key=xxx` | Детали заказа |

---

## **Примеры запросов**

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

### Ответ при ошибке

```json
{
    "success": false,
    "error": {
        "code": "NOT_ENOUGH_STOCK",
        "message": "Недостаточно товара 'Ноутбук'. Доступно: 5"
    }
}
```

---

## **Коды ошибок**

| Код | Описание |
|-----|----------|
| `VALIDATION_ERROR` | Ошибка валидации данных |
| `PRODUCT_NOT_FOUND` | Товар не найден |
| `NOT_ENOUGH_STOCK` | Недостаточно товара на складе |
| `CART_EMPTY` | Корзина пуста |
| `ORDER_NOT_FOUND` | Заказ не найден |
| `PERMISSION_DENIED` | Нет доступа к заказу |
| `INTERNAL_ERROR` | Внутренняя ошибка сервера |


