"""Сервис для работы с товарами"""
from src.shop.domain.models import Product
from src.shop.domain.exceptions import ProductNotFoundError


def get_product(product_id: int) -> Product:
    """Получить товар по ID"""
    try:
        return Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise ProductNotFoundError(f"Товар с id={product_id} не найден")


def get_products(category_id: int = None):
    """Получить список товаров с опциональной фильтрацией по категории"""
    queryset = Product.objects.all()
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    return queryset


def check_stock(product_id: int, required_quantity: int) -> bool:
    """Проверить, достаточно ли товара на складе"""
    product = get_product(product_id)
    return product.stock >= required_quantity