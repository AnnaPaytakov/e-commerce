from django.urls import path
from .views import ProductListView, ProductDetailView, AddToCartView, CartView

urlpatterns = [
    path('', ProductListView.as_view(), name='products-list'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('add-to-cart/<int:pk>/', AddToCartView.as_view(), name='add-to-cart'),
    path('cart/', CartView.as_view(), name='cart-view'),
]