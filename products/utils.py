from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Product
from orders.models import CartItem

class CartMixin(LoginRequiredMixin):
    """Миксин для работы с корзиной"""
    
    def add_to_cart(self, request, pk):
        """Добавление продукта в корзину"""
        product = get_object_or_404(Product, pk=pk)
        cart_item, created = CartItem.objects.get_or_create(user=request.user, product=product)
        if not created:
            cart_item.quantity += 1
            cart_item.save()
        return redirect('cart-view')

    def get_cart_summary(self, request):
        """Получение содержимого корзины и итоговой суммы"""
        cart_items = CartItem.objects.filter(user=request.user)
        total = sum(item.total_price for item in cart_items)
        return {
            'cart_items': cart_items,
            'total': total
        }