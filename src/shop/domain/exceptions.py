"""Доменные исключения для бизнес-логики магазина"""


class DomainError(Exception):
    """Базовое исключение для всех доменных ошибок"""
    pass


class CartEmptyError(DomainError):
    """Корзина пуста"""
    pass


class NotEnoughStockError(DomainError):
    """Недостаточно товара на складе"""
    pass


class ProductNotFoundError(DomainError):
    """Товар не найден"""
    pass


class CartItemNotFoundError(DomainError):
    """Товар в корзине не найден"""
    pass

class OrderNotFoundError(DomainError):
    """Заказ не найден"""
    pass