from fastapi import HTTPException, status, Depends, APIRouter
from models import user_in, Business, User, business_model, user_model, business_in
from dotenv import dotenv_values
from auth import get_current_user

from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import send_email


router = APIRouter(
    prefix="/businesses",
    tags=["Business"]
)


@router.post("/login")
async def user_login(user: user_in = Depends(get_current_user)):
    business = await Business.get(owner=user)
    logo = business.logo
    logo_path = f"localhost:9000/users/static/images/{logo}"

    return {
        "status": "ok",
        "data": {
            "username": user.username,
            "email": user.email,
            "verified": user.is_verified,
            "joined_date": user.join_date.strftime("%d/%m/%Y"),
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
        await business_model.from_tortoise_orm(business_obj)

        await send_email([instance.email], instance)


@router.get("/business")
async def get_businesses():
    response = await business_model.from_queryset(Business.all())
    return {"status": "Successful", "data": response}


@router.get("/business/{id}")
async def get_business(id: int):
    response = await business_model.from_queryset_single(Business.get(id=id))
    return {"status": "Successful", "data": response}

@router.put("/business/{id}")
async def update_business(
        id: int, business_obj: business_in, user: user_model = Depends(get_current_user)
):
    business_obj = business_obj.dict()

    business = await Business.get(id=id)
    business_owner = await business.owner

    if user == business_owner:
        await business.update_from_dict(business_obj)
        await business.save()
        response = await business_model.from_tortoise_orm(business)

        return {"status": "successful", "data": response}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password",
        headers={"WWW-Authenticate": "Bearer"}
    )
