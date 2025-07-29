from django.urls import path
from .views import ProductViewSet, ProductSalesStatsView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'orders', ProductViewSet, basename='order')

urlpatterns = [
    path('stats/', ProductSalesStatsView.as_view(), name='products-stats'),
]