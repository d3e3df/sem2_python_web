"""Бизнес-логика UGC-сервиса"""

import requests
from flask import current_app

from .models import get_db
from .schemas import ReviewCreate, ReviewResponse


def check_product_exists(product_id: int) -> bool:
    """
    Проверить, существует ли товар в Django API.
    Интеграция с основным сервисом.
    """
    try:
        response = requests.get(
            f"{current_app.config['DJANGO_API_URL']}/api/products/{product_id}/",
            timeout=5,
        )
        return response.status_code == 200
    except requests.RequestException:
        return False


def send_notification_to_fastapi(user_id: str, message: str) -> bool:
    """
    Отправить уведомление через FastAPI сервис.
    Возвращает True, если успешно.
    """
    try:
        # Получаем токен из конфига (в реальности — из переменных окружения)
        token = current_app.config.get("FASTAPI_TOKEN", "")
        headers = {"Authorization": f"Bearer {token}"} if token else {}

        response = requests.post(
            f"{current_app.config['FASTAPI_URL']}/notify",
            json={"user_id": user_id, "message": message},
            headers=headers,
            timeout=5,
        )
        return response.status_code == 200
    except requests.RequestException as e:
        current_app.logger.error(f"Ошибка отправки уведомления: {e}")
        return False


def create_review(data: ReviewCreate) -> ReviewResponse:
    """
    Создать новый отзыв.
    Проверяет существование товара через Django API.
    """
    if not check_product_exists(data.product_id):
        raise ValueError(f"Товар с id={data.product_id} не найден")

    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO reviews (product_id, user_id, rating, comment, status)
                VALUES (%s, %s, %s, %s, 'pending')
                RETURNING id
                """,
                (data.product_id, data.user_id, data.rating, data.comment),
            )
            review_id = cur.fetchone()["id"]

            cur.execute("SELECT * FROM reviews WHERE id = %s", (review_id,))
            row = cur.fetchone()
        conn.commit()

    notification_message = f"Новый отзыв на товар {data.product_id}: {data.comment}"
    send_notification_to_fastapi(data.user_id, notification_message)

    return ReviewResponse(
        id=row["id"],
        product_id=row["product_id"],
        user_id=row["user_id"],
        rating=row["rating"],
        comment=row["comment"],
        status=row["status"],
        created_at=str(row["created_at"]),
    )


def get_reviews(product_id: int = None, status: str = None) -> list:
    """
    Получить список отзывов.
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            if product_id and status:
                cur.execute(
                    """
                    SELECT * FROM reviews 
                    WHERE product_id = %s AND status = %s 
                    ORDER BY created_at DESC
                    """,
                    (product_id, status),
                )
            elif product_id:
                cur.execute(
                    """
                    SELECT * FROM reviews 
                    WHERE product_id = %s
                    ORDER BY created_at DESC
                    """,
                    (product_id,),
                )
            elif status:
                cur.execute(
                    "SELECT * FROM reviews WHERE status = %s ORDER BY created_at DESC",
                    (status,),
                )
            else:
                cur.execute("SELECT * FROM reviews ORDER BY created_at DESC")
            rows = cur.fetchall()

    return [
        ReviewResponse(
            id=row["id"],
            product_id=row["product_id"],
            user_id=row["user_id"],
            rating=row["rating"],
            comment=row["comment"],
            status=row["status"],
            created_at=str(row["created_at"]),
        )
        for row in rows
    ]


def update_review_status(review_id: int, status: str) -> ReviewResponse:
    """
    Обновить статус отзыва (для администратора/модератора).
    """
    with get_db() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE reviews SET status = %s WHERE id = %s", (status, review_id)
            )
            cur.execute("SELECT * FROM reviews WHERE id = %s", (review_id,))
            row = cur.fetchone()
        conn.commit()

    if not row:
        raise ValueError(f"Отзыв с id={review_id} не найден")

    return ReviewResponse(
        id=row["id"],
        product_id=row["product_id"],
        user_id=row["user_id"],
        rating=row["rating"],
        comment=row["comment"],
        status=row["status"],
        created_at=str(row["created_at"]),
    )
