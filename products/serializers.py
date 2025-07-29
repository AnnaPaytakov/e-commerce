from rest_framework import serializers
from .models import Product


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ["id", "name", "price", "special_price", "image_url"]


# . statistics for analyzing products sales
class ProductSalesStatsSerializer(serializers.Serializer):
    product_id = serializers.UUIDField(source="product__id")
    product_name = serializers.CharField(source="product__name")
    total_quantity = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        fields = ["product_id", "product_name", "total_quantity", "total_revenue"]
