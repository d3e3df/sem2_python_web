# Спринт 3

## Цель спринта
Реализовать подсистему пользовательского контента (UGC) на Flask с интеграцией с основным Django API.

## Что сделано

### Django (основной сервис)
- Товары, категории, корзина, заказы
- Админка для управления
- REST API с пагинацией и фильтрацией

### Flask (UGC-сервис)
- Отзывы на товары (create, list, update status)
- Валидация через Pydantic V2
- Интеграция с Django: проверка существования товара
- Статусы отзывов: `pending` / `active` / `hidden`
- Единый формат ошибок

## Структура проекта

```
sem2_python_web/
├── config/                 # Django settings
├── shop/                   # Django: товары, корзина, заказы
├── ugc_service/            # Flask: отзывы
│   ├── app.py
│   ├── models.py
│   ├── schemas.py
│   └── services.py
├── tests/                  # Unit-тесты
├── manage.py
└── README.md
```

---

## Запуск проекта

### 1. Запустить Django (порт 8000)

```bash
cd src
python manage.py runserver
```

### 2. Запустить Flask (порт 5001)

```bash
cd ~/PycharmProjects/sem2_python_web
export FLASK_APP=ugc_service.app
export FLASK_ENV=development
flask run --port=5001
```

---

## API эндпоинты

### Django (основной API)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| GET | `/api/products/` | Список товаров |
| GET | `/api/products/{id}/` | Детали товара |
| POST | `/api/cart/` | Добавить в корзину |
| POST | `/api/orders/` | Оформить заказ |

### Flask (UGC-сервис)

| Метод | Эндпоинт | Описание |
|-------|----------|----------|
| POST | `/ugc/reviews/` | Создать отзыв |
| GET | `/ugc/reviews/?product_id=1` | Отзывы по товару |
| GET | `/ugc/reviews/?status=active` | Отзывы по статусу |
| PATCH | `/ugc/reviews/{id}/status` | Изменить статус (admin) |

---

## Примеры запросов

### Создать отзыв

```bash
curl -X POST http://127.0.0.1:5001/ugc/reviews/ \
  -H "Content-Type: application/json" \
  -d '{"product_id": 1, "user_id": "user", "rating": 5, "comment": "Класс"}'
```

### Получить отзывы по товару

```bash
curl "http://127.0.0.1:5001/ugc/reviews/?product_id=1" | jq .
```

### Изменить статус (администратор)

```bash
curl -X PATCH http://127.0.0.1:5001/ugc/reviews/1/status \
  -H "Content-Type: application/json" \
  -d '{"status": "active"}'
```