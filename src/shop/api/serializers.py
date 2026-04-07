from rest_framework import serializers

from shop.domain.models import Cart, Category, Order, OrderItem, Product


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        fields = ["id", "name", "slug"]


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.ReadOnlyField(source="category.name")

    class Meta:
        model = Product
        fields = [
            "id",
            "name",
            "description",
            "price",
            "category",
            "category_name",
            "stock",
        ]


class CartSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")
    product_price = serializers.ReadOnlyField(source="product.price")

    class Meta:
        model = Cart
        fields = ["id", "product", "product_name", "product_price", "quantity"]


class OrderItemSerializer(serializers.ModelSerializer):
    product_name = serializers.ReadOnlyField(source="product.name")

    class Meta:
        model = OrderItem
        fields = ["id", "product", "product_name", "quantity", "price_at_time"]


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = [
            "id",
            "session_key",
            "user_email",
            "status",
            "total_price",
            "items",
            "created_at",
        ]
        read_only_fields = ["total_price", "created_at"]


class CreateOrderSerializer(serializers.Serializer):
    session_key = serializers.CharField(max_length=40)
    user_email = serializers.EmailField(required=False, allow_blank=True)


class AddToCartSerializer(serializers.Serializer):
    session_key = serializers.CharField(max_length=40)
    product = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
