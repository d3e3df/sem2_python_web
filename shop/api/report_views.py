"""Эндпоинты для отчётов"""

from datetime import timedelta

from django.db.models import Sum
from django.utils import timezone
from rest_framework.decorators import api_view
from rest_framework.response import Response

from shop.domain.models import Order, OrderItem


@api_view(["GET"])
def orders_report(request):
    """
    Отчёт по заказам за последние N дней.
    GET /api/orders/report/?days=7
    """
    days = int(request.GET.get("days", 7))
    start_date = timezone.now() - timedelta(days=days)

    orders = Order.objects.filter(created_at__gte=start_date)

    total_orders = orders.count()
    total_revenue = orders.aggregate(total=Sum("total_price"))["total"] or 0

    top_items = (
        OrderItem.objects.filter(order__created_at__gte=start_date)
        .values("product__name")
        .annotate(total_quantity=Sum("quantity"))
        .order_by("-total_quantity")[:5]
    )

    return Response(
        {
            "total_orders": total_orders,
            "total_revenue": float(total_revenue),
            "average_order_value": (
                float(total_revenue / total_orders) if total_orders > 0 else 0
            ),
            "top_products": list(top_items),
        }
    )
