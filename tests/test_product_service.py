"""Unit-тесты для product_service"""
from django.test import TestCase
from shop.domain.models import Category, Product
from shop.services.product_service import get_product, get_products, check_stock
from shop.domain.exceptions import ProductNotFoundError


class ProductServiceTest(TestCase):
    """Тесты сервиса товаров"""

    def setUp(self):
        """Подготовка данных перед каждым тестом"""
        self.category = Category.objects.create(
            name="Электроника",
            slug="electronics"
        )
        self.product = Product.objects.create(
            name="Ноутбук",
            description="Мощный ноутбук",
            price=50000,
            category=self.category,
            stock=10
        )

    def test_get_product_success(self):
        """Тест: получение товара по ID (успех)"""
        product = get_product(self.product.id)
        self.assertEqual(product.name, "Ноутбук")
        self.assertEqual(product.price, 50000)

    def test_get_product_not_found(self):
        """Тест: получение товара по ID (ошибка)"""
        with self.assertRaises(ProductNotFoundError):
            get_product(999)

    def test_get_products_all(self):
        """Тест: получение всех товаров"""
        products = get_products()
        self.assertEqual(products.count(), 1)

    def test_get_products_by_category(self):
        """Тест: фильтрация товаров по категории"""
        # Создаём другую категорию и товар
        category2 = Category.objects.create(name="Книги", slug="books")
        Product.objects.create(
            name="Python для начинающих",
            description="Книга",
            price=2000,
            category=category2,
            stock=5
        )

        # Фильтруем по первой категории
        products = get_products(category_id=self.category.id)
        self.assertEqual(products.count(), 1)
        self.assertEqual(products.first().name, "Ноутбук")

    def test_check_stock_success(self):
        """Тест: проверка наличия (достаточно)"""
        result = check_stock(self.product.id, 5)
        self.assertTrue(result)

    def test_check_stock_fail(self):
        """Тест: проверка наличия (недостаточно)"""
        result = check_stock(self.product.id, 20)
        self.assertFalse(result)