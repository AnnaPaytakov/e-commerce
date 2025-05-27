from django.views import View
from django.contrib.auth.mixins import UserPassesTestMixin
from django.shortcuts import render

class AdminOrdersView(UserPassesTestMixin, View):
    def test_func(self):
        return self.request.user.is_superuser

    def get(self, request):
        return render(request, 'orders/orders.html')