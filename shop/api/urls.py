from django.urls import include, path
from rest_framework.routers import DefaultRouter

from shop.api.views import (CartViewSet, CategoryViewSet, OrderViewSet,
                            ProductViewSet)

from .report_views import orders_report

router = DefaultRouter()
router.register(r"categories", CategoryViewSet, basename="category")
router.register(r"products", ProductViewSet, basename="product")
router.register(r"cart", CartViewSet, basename="cart")
router.register(r"orders", OrderViewSet, basename="order")

urlpatterns = [
    path("orders/report/", orders_report, name="orders_report"),
    path("", include(router.urls)),
]
