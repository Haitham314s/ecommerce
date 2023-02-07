from tortoise import Model, fields
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True, index=True)
    email = fields.CharField(max_length=200, null=False, unique=True, index=True)
    password = fields.CharField(max_length=100, null=False, index=True)
    is_verified = fields.BooleanField(default=False, index=True)
    join_date = fields.DatetimeField(default=datetime.utcnow, index=True)


user_model = pydantic_model_creator(User, name="User", exclude=("is_verified",))
user_in = pydantic_model_creator(User, name="UserIn", exclude_readonly=True,
                                         exclude=("is_verified", "join_date"))
user_out = pydantic_model_creator(User, name="UserOut", exclude=("password",))
