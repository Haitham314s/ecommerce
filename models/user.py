from tortoise import Model, fields
from datetime import datetime
from tortoise.contrib.pydantic import pydantic_model_creator


class User(Model):
    id = fields.IntField(pk=True, index=True)
    username = fields.CharField(max_length=20, null=False, unique=True)
    email = fields.CharField(max_length=200, null=False, unique=True)
    password = fields.CharField(max_length=100, null=False)
    is_verified = fields.BooleanField(default=False)
    join_date = fields.DatetimeField(default=datetime.utcnow)


user_pydantic = pydantic_model_creator(User, name="User", exclude=("is_verified",))
user_pydanticIn = pydantic_model_creator(User, name="UserIn", exclude_readonly=True,
                                         exclude=("is_verified", "join_date"))
user_pydanticOut = pydantic_model_creator(User, name="UserOut", exclude=("password",))
