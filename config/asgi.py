import os
import django
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

# Устанавливаем DJANGO_SETTINGS_MODULE и инициализируем настройки
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Теперь безопасно импортировать routing
import orders.routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(orders.routing.websocket_urlpatterns)
    ),
})

print("ASGI serwer ishledi")