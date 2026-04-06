"""Сервис для работы с корзиной"""
from src.shop.domain.models import Cart, Product
from src.shop.domain.exceptions import ProductNotFoundError, NotEnoughStockError


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

    # Проверяем наличие на складе
    if product.stock < quantity:
        raise NotEnoughStockError(
            f"Недостаточно товара '{product.name}'. Доступно: {product.stock}"
        )

    # Добавляем или обновляем корзину
    cart_item, created = Cart.objects.get_or_create(
        session_key=session_key,
        product=product,
        defaults={'quantity': quantity}
    )
    if not created:
        cart_item.quantity += quantity
        cart_item.save()

    return cart_item


def get_cart(session_key: str):
    """Получить все товары в корзине"""
    return Cart.objects.filter(session_key=session_key)


def clear_cart(session_key: str) -> None:
    """Очистить корзину"""
    Cart.objects.filter(session_key=session_key).delete()