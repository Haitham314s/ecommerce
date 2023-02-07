from tortoise import Model, fields
from tortoise.contrib.pydantic import pydantic_model_creator


class Business(Model):
    id = fields.IntField(pk=True, index=True)
    business_name = fields.CharField(max_length=20, null=False, unique=True, index=True)
    city = fields.CharField(max_length=100, null=False, default="Unspecified", index=True)
    region = fields.CharField(max_length=100, null=False, default="Unspecified", index=True)
    business_description = fields.TextField(null=True)
    logo = fields.CharField(max_length=200, null=False, default="default.jpg", index=True)
    owner = fields.ForeignKeyField("models.User", related_name="business", index=True)


business_model = pydantic_model_creator(Business, name="Business")
business_in = pydantic_model_creator(Business, name="Business", exclude_readonly=True)
