from django.db import transaction
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Cart, Category, Order, OrderItem, Product
from .serializers import (CartSerializer, CategorySerializer,
                          CreateOrderSerializer, OrderSerializer,
                          ProductSerializer)


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Чтение списка категорий"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Список и детали товаров с фильтрацией по категории"""

    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        # Фильтрация по категории: /api/products/?category=1
        category_id = self.request.query_params.get("category")
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class CartViewSet(viewsets.GenericViewSet):
    """Работа с корзиной"""

    serializer_class = CartSerializer

    def get_queryset(self):
        session_key = self.request.query_params.get("session_key")
        if session_key:
            return Cart.objects.filter(session_key=session_key)
        return Cart.objects.none()

    def create(self, request):
        """POST /api/cart/ — добавить товар в корзину"""
        session_key = request.data.get("session_key")
        product_id = request.data.get("product")
        quantity = request.data.get("quantity", 1)

        # Валидация
        if not session_key or not product_id:
            return Response(
                {"error": "session_key и product обязательны"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Проверяем существование товара
        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response(
                {"error": "Товар не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        # Проверяем наличие на складе
        if product.stock < quantity:
            return Response(
                {"error": f"Недостаточно товара на складе. Доступно: {product.stock}"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Добавляем или обновляем корзину
        cart_item, created = Cart.objects.get_or_create(
            session_key=session_key, product=product, defaults={"quantity": quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()

        serializer = self.get_serializer(cart_item)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """GET /api/cart/?session_key=xxx — получить корзину"""
        session_key = request.query_params.get("session_key")
        if not session_key:
            return Response(
                {"error": "session_key обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        cart_items = Cart.objects.filter(session_key=session_key)
        serializer = self.get_serializer(cart_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        """DELETE /api/cart/clear/?session_key=xxx — очистить корзину"""
        session_key = request.query_params.get("session_key")
        if not session_key:
            return Response(
                {"error": "session_key обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        Cart.objects.filter(session_key=session_key).delete()
        return Response({"message": "Корзина очищена"}, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.GenericViewSet):
    """Работа с заказами"""

    serializer_class = OrderSerializer

    def get_queryset(self):
        session_key = self.request.query_params.get("session_key")
        if session_key:
            return Order.objects.filter(session_key=session_key)
        return Order.objects.none()

    def create(self, request):
        """POST /api/orders/ — создать заказ из корзины"""
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        session_key = serializer.validated_data["session_key"]
        user_email = serializer.validated_data.get("user_email", "")

        # Получаем корзину
        cart_items = Cart.objects.filter(session_key=session_key)
        if not cart_items.exists():
            return Response(
                {"error": "Корзина пуста"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Проверяем наличие всех товаров
        for item in cart_items:
            if item.product.stock < item.quantity:
                return Response(
                    {
                        "error": f'Недостаточно товара "{item.product.name}". Доступно: {item.product.stock}'
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )

        with transaction.atomic():
            total_price = sum(item.product.price * item.quantity for item in cart_items)

            # Создаём заказ
            order = Order.objects.create(
                session_key=session_key,
                user_email=user_email,
                total_price=total_price,
                status="pending",
            )

            # Создаём позиции заказа
            for item in cart_items:
                OrderItem.objects.create(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    price_at_time=item.product.price,
                )
                # Уменьшаем количество на складе
                item.product.stock -= item.quantity
                item.product.save()

            # Очищаем корзину
            cart_items.delete()

        # Возвращаем созданный заказ
        order_serializer = OrderSerializer(order)
        return Response(order_serializer.data, status=status.HTTP_201_CREATED)

    def list(self, request):
        """GET /api/orders/?session_key={} — получить заказы пользователя"""
        session_key = request.query_params.get("session_key")
        if not session_key:
            return Response(
                {"error": "session_key обязателен"}, status=status.HTTP_400_BAD_REQUEST
            )

        orders = Order.objects.filter(session_key=session_key).order_by("-created_at")
        serializer = self.get_serializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/orders/{id}/ — получить детали заказа"""
        try:
            order = Order.objects.get(id=pk)
        except Order.DoesNotExist:
            return Response(
                {"error": "Заказ не найден"}, status=status.HTTP_404_NOT_FOUND
            )

        serializer = self.get_serializer(order)
        return Response(serializer.data)
