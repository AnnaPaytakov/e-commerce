import logging
from .models import Order, OrderItem
from products.models import Product
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

logger = logging.getLogger(__name__)


class OrderHandlerMixin:
    # Creatting an order with a product and sending it via WebSocket
    def create_order(self, user, data):
        logger.info("=== START CREATE ORDER ===")
        logger.info(f"User: {user}")

        try:
            name = data.get("name")
            price = float(data.get("price", 0))
            special_price = data.get("special_price")
            if not name or price <= 0:
                logger.error("Invalid order data: name or price missing/invalid")
                return None, "Invalid order data"

            # create product
            product = Product.objects.create(
                name=name,
                price=price,
                special_price=float(special_price)
                if special_price is not None
                else None,
            )
            logger.info(f"Created product: {product.name}")

            # make order
            order = Order.objects.create(user=user)
            logger.info(f"Order created with ID: {order.id}")

            # create order item
            OrderItem.objects.create(order=order, product=product, quantity=1)
            logger.info(f"Added order item: 1x {product.name}")

            # Prepare order data for WebSocket
            user_identifier = f"{user.full_name} ({user.phone})"
            order_data = {
                "id": order.id,
                "user": user_identifier,
                "created_at": order.created_at.isoformat(),
                "items": [{"product_name": product.name, "quantity": 1}],
            }
            logger.info(f"Order data: {order_data}")

            # Send order data via WebSocket
            try:
                channel_layer = get_channel_layer()
                if channel_layer:
                    message = {"type": "send_order", "order": order_data}
                    async_to_sync(channel_layer.group_send)("orders", message)
                    logger.info("WebSocket message sent successfully")
                else:
                    logger.error("Channel layer not available")
                    return None, "Channel layer not available"
            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                return None, f"WebSocket error: {e}"

            logger.info("=== END CREATE ORDER ===")
            return order, None
        except Exception as e:
            logger.error(f"Order creation error: {e}")
            return None, str(e)
