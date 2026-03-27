from django.contrib import admin

from .models import Cart, Category, Order, OrderItem, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "price", "category", "stock", "created_at")
    list_filter = ("category", "created_at")
    search_fields = ("name",)


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ("session_key", "product", "quantity", "created_at")
    search_fields = ("session_key",)
    list_filter = ("created_at",)


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "session_key",
        "user_email",
        "status",
        "total_price",
        "created_at",
    )
    list_filter = ("status", "created_at")
    search_fields = ("session_key", "user_email")
    readonly_fields = ("total_price", "created_at", "updated_at")


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("order", "product", "quantity", "price_at_time")
    list_filter = ("order",)
    search_fields = ("product__name",)
