from tortoise import Model, fields
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator

class Product(Model):
    id = fields.IntField(pk=True, index=True)
    name = fields.CharField(max_length=100, null=False, index=True)
    category = fields.CharField(max_length=30, index=True)

    original_price = fields.DecimalField(max_digits=20, decimal_places=2, default=0.00, index=True)
    new_price = fields.DecimalField(max_digits=20, decimal_places=2, default=0.00, index=True)
    percentage_discount = fields.IntField()

    quantity_in_stock = fields.IntField(default=0, index=True)
    quantity_sold = fields.IntField(default=0, index=True)
    revenue = fields.DecimalField(max_digits=20, decimal_places=2, default=0, index=True)

    offer_expiration_date = fields.DateField(default=datetime.utcnow, index=True)
    product_image = fields.CharField(max_length=200, null=False, default="productDefault.jpg", index=True)
    date_published = fields.DatetimeField(default=datetime.utcnow, index=True)
    business = fields.ForeignKeyField("models.Business", related_name="products", index=True)


product_model = pydantic_model_creator(Product, name="Product")
product_in = pydantic_model_creator(
    Product, name="ProductIn",
    exclude=("percentage_discount", "id", "product_image", "date_published", "quantity_in_stock", "quantity_sold",
             "revenue")
)
