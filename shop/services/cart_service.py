"""Сервис для работы с корзиной"""

from django.db import transaction

from shop.domain.exceptions import NotEnoughStockError, ProductNotFoundError
from shop.domain.models import Cart, Product


def add_to_cart(session_key: str, product_id: int, quantity: int = 1) -> Cart:
    """
    Добавить товар в корзину.
    Возвращает объект Cart.
    """
    # Проверяем существование товара
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise ProductNotFoundError(f"Товар с id={product_id} не найден")

    with transaction.atomic():
        # Получаем текущее количество в корзине (если есть)
        cart_item, created = Cart.objects.get_or_create(
            session_key=session_key,
            product=product,
            defaults={"quantity": 0},
        )

        # Итоговое количество после добавления
        total_quantity = cart_item.quantity + quantity

        # Проверяем наличие на складе
        if product.stock < total_quantity:
            raise NotEnoughStockError(
                f"Недостаточно товара '{product.name}'. В корзине уже {cart_item.quantity}, "
                f"доступно: {product.stock}"
            )

        # Обновляем количество
        cart_item.quantity = total_quantity
        cart_item.save()

        return cart_item


def get_cart(session_key: str):
    """Получить все товары в корзине"""
    return Cart.objects.filter(session_key=session_key)


def clear_cart(session_key: str) -> None:
    """Очистить корзину"""
    Cart.objects.filter(session_key=session_key).delete()
