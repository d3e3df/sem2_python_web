"""Тесты для cart_service"""

from django.test import TestCase

from shop.domain.exceptions import NotEnoughStockError, ProductNotFoundError
from shop.domain.models import Cart, Category, Product
from shop.services.cart_service import add_to_cart, clear_cart, get_cart


class CartServiceTest(TestCase):
    """Тесты сервиса корзины"""

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

    def test_add_to_cart_new_item(self):
        """Тест: добавление нового товара в корзину"""
        cart_item = add_to_cart(self.session_key, self.product.id, 2)

        self.assertEqual(cart_item.product.name, "Ноутбук")
        self.assertEqual(cart_item.quantity, 2)
        self.assertEqual(cart_item.session_key, self.session_key)

        # Проверяем, что запись создалась в БД
        self.assertEqual(Cart.objects.count(), 1)

    def test_add_to_cart_existing_item(self):
        """Тест: добавление товара, который уже есть в корзине"""
        # Первое добавление
        add_to_cart(self.session_key, self.product.id, 2)
        # Второе добавление
        cart_item = add_to_cart(self.session_key, self.product.id, 3)

        # Количество должно сложиться: 2 + 3 = 5
        self.assertEqual(cart_item.quantity, 5)
        self.assertEqual(Cart.objects.count(), 1)  # Запись всё ещё одна

    def test_add_to_cart_not_enough_stock(self):
        """Тест: добавление товара в количестве больше, чем на складе"""
        with self.assertRaises(NotEnoughStockError):
            add_to_cart(self.session_key, self.product.id, 20)

    def test_add_to_cart_product_not_found(self):
        """Тест: добавление несуществующего товара"""
        with self.assertRaises(ProductNotFoundError):
            add_to_cart(self.session_key, 999, 1)

    def test_get_cart(self):
        """Тест: получение корзины"""
        add_to_cart(self.session_key, self.product.id, 3)

        cart_items = get_cart(self.session_key)
        self.assertEqual(cart_items.count(), 1)
        self.assertEqual(cart_items.first().quantity, 3)

    def test_get_cart_empty(self):
        """Тест: получение пустой корзины"""
        cart_items = get_cart("non_existent_session")
        self.assertEqual(cart_items.count(), 0)

    def test_clear_cart(self):
        """Тест: очистка корзины"""
        add_to_cart(self.session_key, self.product.id, 2)
        self.assertEqual(Cart.objects.count(), 1)

        clear_cart(self.session_key)
        self.assertEqual(Cart.objects.count(), 0)
