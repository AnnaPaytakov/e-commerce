from django.contrib import admin
from django.urls import path, include
from api.views import CustomTokenObtainPairView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', include('products.urls')),
    path('api/', include('api.urls')),
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('users/', include('users.urls')),
    path('orders/', include('orders.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)