from django_filters.rest_framework import DjangoFilterBackend
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from rest_framework import viewsets


from rest_framework.permissions import IsAdminUser
from rest_framework.views import APIView

from rest_framework.response import Response

from rest_framework.permissions import AllowAny
from .models import Product
from .filters import ProductFilter
from .serializers import ProductSerializer, ProductSalesStatsSerializer

from django.db.models import Sum, F
from django.db.models.functions import Coalesce
from django.utils import timezone
from datetime import timedelta
from orders.models import OrderItem

import logging

logger = logging.getLogger(__name__)


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = ProductFilter

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminUser()]
        return [AllowAny()]

    @method_decorator(cache_page(60 * 15))  #! Cache for 15 minutes
    def list(self, request, *args, **kwargs):
        logger.debug("ProductViewSet.list called, checking cache")
        response = super().list(request, *args, **kwargs)
        logger.debug("ProductViewSet.list response generated")
        return response

    @method_decorator(cache_page(60 * 15))  #! Cache for 15 minutes
    def retrieve(self, request, *args, **kwargs):
        logger.debug("ProductViewSet.retrieve called, checking cache")
        response = super().retrieve(request, *args, **kwargs)
        logger.debug("ProductViewSet.retrieve response generated")
        return response


class ProductSalesStatsView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        month = request.query_params.get("month")
        if month:
            try:
                year, month = map(int, month.split("-"))
                start_date = timezone.datetime(year, month, 1)
                end_date = (start_date + timedelta(days=31)).replace(day=1) - timedelta(
                    seconds=1
                )
            except ValueError:
                return Response(
                    {"error": "Invalid month format. Use YYYY-MM."}, status=400
                )
        else:
            end_date = timezone.now()
            start_date = end_date - timedelta(days=30)

        stats = (
            OrderItem.objects.filter(
                order__created_at__range=[start_date, end_date], order__is_paid=True
            )
            .values("product__id", "product__name")
            .annotate(
                total_quantity=Sum("quantity"),
                total_revenue=Sum(
                    F("quantity")
                    * Coalesce(F("product__special_price"), F("product__price"))
                ),
            )
        )

        if not stats:
            return Response([])

        serializer = ProductSalesStatsSerializer(stats, many=True)
        return Response(serializer.data)
