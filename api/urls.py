from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    UserSignupView, MeView, UserListView, UserCreateView, UserUpdateView, UserDeleteView,
    ProductViewSet, OrderViewSet, ProductSalesStatsView, LogoutView
)

router = DefaultRouter()
router.register(r'products', ProductViewSet, basename='product')
router.register(r'orders', OrderViewSet, basename='order')

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('users/me/', MeView.as_view(), name='me'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/create/', UserCreateView.as_view(), name='user-create'),
    path('users/<uuid:pk>/', UserUpdateView.as_view(), name='user-update'),
    path('users/<uuid:pk>/delete/', UserDeleteView.as_view(), name='user-delete'),
    path('stats/products/', ProductSalesStatsView.as_view(), name='product-stats'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('', include(router.urls)),
]