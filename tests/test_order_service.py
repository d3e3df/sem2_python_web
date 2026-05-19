"""Unit-тесты для order_service"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from django.test import TestCase

from shop.domain.exceptions import (CartEmptyError, NotEnoughStockError,
                                    OrderNotFoundError)
from shop.domain.models import Cart, Category, Order, OrderItem, Product
from shop.services.cart_service import add_to_cart, get_cart
from shop.services.order_service import (create_order, get_order_by_id,
                                         get_orders)


class OrderServiceTest(TestCase):
    """Тесты сервиса заказов"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.category = Category.objects.create(name="Электроника", slug="electronics")
        self.product = Product.objects.create(
            name="Ноутбук",
            description="Мощный ноутбук",
            price=50000,
            category=self.category,
            stock=10,
        )
        self.session_key = "test_session_123"

    def test_create_order_success(self):
        """Тест: успешное создание заказа из корзины"""
        # Добавляем товар в корзину
        add_to_cart(self.session_key, self.product.id, 2)

        # Создаём заказ
        order = create_order(self.session_key, "test@example.com")

        # Проверяем заказ
        self.assertEqual(order.session_key, self.session_key)
        self.assertEqual(order.user_email, "test@example.com")
        self.assertEqual(order.status, "pending")
        self.assertEqual(order.total_price, 100000)  # 2 * 50000

        # Проверяем позиции заказа
        self.assertEqual(order.items.count(), 1)
        self.assertEqual(order.items.first().quantity, 2)
        self.assertEqual(order.items.first().price_at_time, 50000)

        # Проверяем, что корзина очистилась
        self.assertEqual(Cart.objects.count(), 0)

        # Проверяем, что stock уменьшился
        self.product.refresh_from_db()
        self.assertEqual(self.product.stock, 8)  # Было 10, купили 2

    def test_create_order_empty_cart(self):
        """Тест: создание заказа из пустой корзины"""
        with self.assertRaises(CartEmptyError):
            create_order(self.session_key, "test@example.com")

    def test_create_order_not_enough_stock(self):
        """Тест: создание заказа, когда товара недостаточно"""
        # Попытка добавить больше, чем есть на складе → ошибка при добавлении
        with self.assertRaises(NotEnoughStockError):
            add_to_cart(self.session_key, self.product.id, 20)

        # Корзина должна остаться пустой
        self.assertEqual(get_cart(self.session_key).count(), 0)

    def test_get_orders(self):
        """Тест: получение списка заказов пользователя"""
        # Создаём два заказа
        add_to_cart(self.session_key, self.product.id, 1)
        create_order(self.session_key, "test@example.com")

        add_to_cart(self.session_key, self.product.id, 2)
        create_order(self.session_key, "test@example.com")

        orders = get_orders(self.session_key)
        self.assertEqual(orders.count(), 2)

    def test_get_order_by_id_success(self):
        """Тест: получение заказа по ID"""
        add_to_cart(self.session_key, self.product.id, 1)
        created_order = create_order(self.session_key, "test@example.com")

        order = get_order_by_id(created_order.id, self.session_key)
        self.assertEqual(order.id, created_order.id)

    def test_get_order_by_id_not_found(self):
        """Тест: получение несуществующего заказа"""
        with self.assertRaises(OrderNotFoundError):
            get_order_by_id(999, self.session_key)

    def test_get_order_by_id_wrong_session(self):
        """Тест: попытка получить чужой заказ"""
        add_to_cart(self.session_key, self.product.id, 1)
        created_order = create_order(self.session_key, "test@example.com")

        with self.assertRaises(PermissionError):
            get_order_by_id(created_order.id, "wrong_session")
