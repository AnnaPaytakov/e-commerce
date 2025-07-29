from django.db import models
import uuid


class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    special_price = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )
    image_url = models.ImageField(upload_to="giper_images/")
    id = models.UUIDField(
        default=uuid.uuid4, unique=True, editable=False, primary_key=True
    )

    def __str__(self):
        return self.name
