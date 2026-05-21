"""HTTP слой"""

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from shop.api.serializers import (AddToCartSerializer, CartSerializer,
                                  CategorySerializer, CreateOrderSerializer,
                                  OrderSerializer, ProductSerializer)
from shop.domain.exceptions import (CartEmptyError, NotEnoughStockError,
                                    OrderNotFoundError, ProductNotFoundError)
from shop.domain.models import Category
from shop.services.cart_service import add_to_cart, clear_cart, get_cart
from shop.services.order_service import (create_order, get_order_by_id,
                                         get_orders)
from shop.services.product_service import get_product, get_products


def error_response(message, code="ERROR", status_code=status.HTTP_400_BAD_REQUEST):
    """Единый формат ошибок"""
    return Response(
        {
            "success": False,
            "error": {
                "code": code,
                "message": message,
            },
        },
        status=status_code,
    )


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    """Чтение списка категорий"""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class ProductViewSet(viewsets.ReadOnlyModelViewSet):
    """Список и детали товаров с фильтрацией по категории"""

    def get_queryset(self):
        category_id = self.request.query_params.get("category")
        return get_products(category_id)

    def get_serializer_class(self):
        return ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        """Получить детали товара"""
        try:
            product = get_product(kwargs["pk"])
            serializer = self.get_serializer(product)
            return Response(serializer.data)
        except ProductNotFoundError as e:
            return error_response(
                str(e), "PRODUCT_NOT_FOUND", status.HTTP_404_NOT_FOUND
            )


class CartViewSet(viewsets.GenericViewSet):
    """Работа с корзиной"""

    def get_serializer_class(self):
        return CartSerializer

    def create(self, request):
        """POST /api/cart/ — добавить товар в корзину"""
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                serializer.errors, "VALIDATION_ERROR", status.HTTP_400_BAD_REQUEST
            )

        try:
            cart_item = add_to_cart(
                session_key=serializer.validated_data["session_key"],
                product_id=serializer.validated_data["product"],
                quantity=serializer.validated_data["quantity"],
            )
            return Response(
                CartSerializer(cart_item).data, status=status.HTTP_201_CREATED
            )
        except ProductNotFoundError as e:
            return error_response(
                str(e), "PRODUCT_NOT_FOUND", status.HTTP_404_NOT_FOUND
            )
        except NotEnoughStockError as e:
            return error_response(
                str(e), "NOT_ENOUGH_STOCK", status.HTTP_400_BAD_REQUEST
            )

    def list(self, request):
        """GET /api/cart/?session_key=xxx — получить корзину"""
        session_key = request.query_params.get("session_key")
        if not session_key:
            return error_response(
                "session_key обязателен",
                "MISSING_SESSION_KEY",
                status.HTTP_400_BAD_REQUEST,
            )

        cart_items = get_cart(session_key)
        serializer = CartSerializer(cart_items, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=["delete"])
    def clear(self, request):
        """DELETE /api/cart/clear/?session_key=xxx — очистить корзину"""
        session_key = request.query_params.get("session_key")
        if not session_key:
            return error_response(
                "session_key обязателен",
                "MISSING_SESSION_KEY",
                status.HTTP_400_BAD_REQUEST,
            )

        clear_cart(session_key)
        return Response({"message": "Корзина очищена"}, status=status.HTTP_200_OK)


class OrderViewSet(viewsets.GenericViewSet):
    """Работа с заказами"""

    def get_serializer_class(self):
        return OrderSerializer

    def create(self, request):
        """POST /api/orders/ — создать заказ из корзины"""
        serializer = CreateOrderSerializer(data=request.data)
        if not serializer.is_valid():
            return error_response(
                serializer.errors, "VALIDATION_ERROR", status.HTTP_400_BAD_REQUEST
            )

        try:
            order = create_order(
                session_key=serializer.validated_data["session_key"],
                user_email=serializer.validated_data.get("user_email", ""),
            )
            return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)
        except CartEmptyError as e:
            return error_response(str(e), "CART_EMPTY", status.HTTP_400_BAD_REQUEST)
        except NotEnoughStockError as e:
            return error_response(
                str(e), "NOT_ENOUGH_STOCK", status.HTTP_400_BAD_REQUEST
            )

    def list(self, request):
        """GET /api/orders/?session_key=xxx — получить заказы пользователя"""
        session_key = request.query_params.get("session_key")
        if not session_key:
            return error_response(
                "session_key обязателен",
                "MISSING_SESSION_KEY",
                status.HTTP_400_BAD_REQUEST,
            )

        orders = get_orders(session_key)
        serializer = OrderSerializer(orders, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        """GET /api/orders/{id}/ — получить детали заказа"""
        session_key = request.query_params.get("session_key")
        if not session_key:
            return error_response(
                "session_key обязателен",
                "MISSING_SESSION_KEY",
                status.HTTP_400_BAD_REQUEST,
            )

        try:
            order = get_order_by_id(pk, session_key)
            serializer = OrderSerializer(order)
            return Response(serializer.data)
        except OrderNotFoundError as e:
            return error_response(str(e), "ORDER_NOT_FOUND", status.HTTP_404_NOT_FOUND)
        except PermissionError as e:
            return error_response(
                str(e), "PERMISSION_DENIED", status.HTTP_403_FORBIDDEN
            )
