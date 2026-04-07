"""Сервис для работы с заказами"""

from django.db import transaction

from shop.domain.exceptions import (CartEmptyError, NotEnoughStockError,
                                    OrderNotFoundError)
from shop.domain.models import Order, OrderItem
from shop.services.cart_service import clear_cart, get_cart


def create_order(session_key: str, user_email: str = "") -> Order:
    """
    Создать заказ из корзины.
    Возвращает объект Order.
    """
    cart_items = get_cart(session_key)

    # Проверяем, что корзина не пуста
    if not cart_items.exists():
        raise CartEmptyError("Корзина пуста")

    # Проверяем наличие всех товаров
    for item in cart_items:
        if item.product.stock < item.quantity:
            raise NotEnoughStockError(
                f"Недостаточно товара '{item.product.name}'. Доступно: {item.product.stock}"
            )

    # Создаём заказ в транзакции
    with transaction.atomic():
        # Вычисляем итоговую сумму
        total_price = sum(item.product.price * item.quantity for item in cart_items)

        # Создаём заказ
        order = Order.objects.create(
            session_key=session_key,
            user_email=user_email,
            total_price=total_price,
            status="pending",
        )

        # Создаём позиции заказа и уменьшаем stock
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price_at_time=item.product.price,
            )
            item.product.stock -= item.quantity
            item.product.save()

        # Очищаем корзину
        clear_cart(session_key)

    return order


def get_orders(session_key: str):
    """Получить все заказы пользователя"""
    return Order.objects.filter(session_key=session_key).order_by("-created_at")


def get_order_by_id(order_id: int, session_key: str = None) -> Order:
    """
    Получить заказ по ID.
    Если передан session_key, проверяется принадлежность заказа пользователю.
    """
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        raise OrderNotFoundError(f"Заказ с id={order_id} не найден")

    if session_key and order.session_key != session_key:
        raise PermissionError("Нет доступа к этому заказу")

    return order
