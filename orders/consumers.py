import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth.models import AnonymousUser
from .utils import OrderHandlerMixin

logger = logging.getLogger(__name__)

class OrderConsumer(AsyncWebsocketConsumer, OrderHandlerMixin):
    async def connect(self):
        logger.info(f"WebSocket connect attempt: {self.channel_name}")
        print(f"Consumer: WebSocket connect attempt: {self.channel_name}")
        
        headers = dict(self.scope['headers'])
        auth_header = headers.get(b'authorization', b'').decode()
        token_key = None
        if auth_header.startswith('Bearer '):
            token_key = auth_header[7:].strip()
        
        logger.info(f"Extracted token: {token_key}")
        
        user = await self.get_user_from_token(token_key)
        
        if user is None or user.is_anonymous:
            logger.warning("Invalid or missing token, closing connection")
            await self.close(code=4001) 
            return
        
        self.scope['user'] = user
        logger.info(f"User authenticated: {user}")
        
        await self.channel_layer.group_add("orders", self.channel_name)
        await self.accept()
        logger.info(f"WebSocket connection accepted: {self.channel_name}")
        print(f"Consumer: WebSocket connection accepted: {self.channel_name}")

    async def disconnect(self, close_code):
        logger.info(f"WebSocket disconnected with code: {close_code}, channel: {self.channel_name}")
        print(f"Consumer: WebSocket disconnected with code: {close_code}, channel: {self.channel_name}")
        await self.channel_layer.group_discard("orders", self.channel_name)

    async def receive(self, text_data):
        logger.info(f"Received WebSocket message: {text_data}")
        print(f"Consumer: Received WebSocket message: {text_data}")
        try:
            data = json.loads(text_data)
            message_type = data.get("type")
            
            if message_type == "create_order":
                order, error = await database_sync_to_async(self.create_order)(self.scope['user'], data)
                if error:
                    await self.send(text_data=json.dumps({"error": error}))
                else:
                    await self.send(text_data=json.dumps({"message": f"Order {order.id} created"}))
            else:
                await self.send(text_data=json.dumps({"error": "Invalid message type"}))
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON: {e}")
            await self.send(text_data=json.dumps({"error": "Invalid JSON"}))
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            await self.send(text_data=json.dumps({"error": str(e)}))

    async def send_order(self, event):
        logger.info(f"Received event: {event}")
        print(f"Consumer: Received event: {event}")
        try:
            order_data = event["order"]
            logger.info(f"Sending order data: {order_data}")
            print(f"Consumer: Sending order data: {order_data}")
            await self.send(text_data=json.dumps({
                "order": order_data
            }))
            logger.info("Order sent successfully")
            print("Consumer: Order sent successfully")
        except Exception as e:
            logger.error(f"Error sending order: {e}")
            print(f"Consumer: Error sending order: {e}")

    @database_sync_to_async
    def get_user_from_token(self, token_key):
        from django.contrib.auth import get_user_model
        try:
            if not token_key:
                logger.error("No token provided")
                return AnonymousUser()
            
            # Валидация JWT
            token = AccessToken(token_key)
            user_id = token['user_id']
            User = get_user_model()
            user = User.objects.get(id=user_id)
            logger.info(f"JWT token validated for user: {user}")
            return user
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            return AnonymousUser()