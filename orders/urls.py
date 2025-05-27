from django.urls import path
from .views import AdminOrdersView

urlpatterns = [
    path('admin/', AdminOrdersView.as_view(), name='admin-orders'),
]