from fastapi import HTTPException, status, Depends
from models.business import *
from models.user import *
from dotenv import dotenv_values
from fastapi.security import OAuth2PasswordBearer
from auth import get_current_user
# Signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import send_email
# Images
from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles

config_credentials = dotenv_values(".env")

router = APIRouter(
    prefix="/businesses",
    tags=["Business"]
)


@router.post("/user/me")
async def user_login(user: user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(owner=user)
    logo = business.logo
    logo_path = f"localhost:9000/static/images/{logo}"

    return {
        "status": "ok",
        "data": {
            "username": user.username,
            "email": user.email,
            "verified": user.is_verified,
            "joined_date": user.join_date.strftime("%b/%d/%Y"),
            "logo": logo_path
        }
    }


@post_save(User)
async def create_business(
        sender: "Type[User]",
        instance: User,
        created: bool,
        using_db: "Optional[BaseDBAsyncClient]",
        update_fields: List[str]
) -> None:
    if created:
        business_obj = await Business.create(
            business_name=instance.username,
            owner=instance
        )
        await business_pydantic.from_tortoise_orm(business_obj)

        # Send the email verification
        await send_email([instance.email], instance)


@router.put("/business/{id}")
async def update_business(
        id: int, update_business: business_pydanticIn, user: user_pydantic = Depends(get_current_user)
):
    update_business = update_business.dict()

    business = await Business.get(id=id)
    business_owner = await business.owner

    if user == business_owner:
        await business.update_from_dict(update_business)
        await business.save()
        response = await business_pydantic.from_tortoise_orm(business)

        return {"status": "successful", "data": response}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password",
        headers={"WWW-Authenticate": "Bearer"}
    )
