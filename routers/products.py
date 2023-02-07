from models import user_pydantic, Product, product_pydanticIn, product_pydantic
from dotenv import dotenv_values
import datetime
from auth import get_current_user

from fastapi import File, UploadFile, APIRouter, HTTPException, status, Depends
from starlette.applications import Starlette
from starlette.staticfiles import StaticFiles
from starlette.routing import Mount

import secrets
from PIL import Image

config_credentials = dotenv_values(".env")

router = APIRouter(
    prefix="/products",
    tags=["Product"]
)

app = Starlette(routes=[
    Mount('/static', StaticFiles(directory='static'))
])


@router.post("/upload_file/product/{id}")
async def create_product_file(
        id: int,
        file: UploadFile = File(...),
        user: user_pydantic = Depends(get_current_user)
):
    filename = file.filename
    extension = filename.split(".")[1]

    if extension not in ["png", "jpg"]:
        return {"status": "error", "detail": "File extension not supported"}

    token_name = f"{secrets.token_hex(10)}.{extension}"
    generated_name = f"./products/static/images/{token_name}"
    file_content = await file.read()
    with open(generated_name, "wb") as file:
        file.write(file_content)

    img = Image.open(generated_name)
    img = img.resize(size=(200, 200))
    img.save(generated_name)

    file.close()

    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner

    if owner != user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated to perform this action",
            headers={"WWW-Authenticate": "Bearer"}
        )

    product.product_image = token_name
    await product.save()

    file_url = f"localhost:9000{generated_name[1:]}"
    return {"status": "successful", "filename": file_url}


# CRUD Functionality
@router.post("/products")
async def add_product(
        product: product_pydanticIn,
        user: user_pydantic = Depends(get_current_user)
):
    product = product.dict(exclude_unset=True)

    if product["original_price"] > 0:
        product["percentage_discount"] = ((product["original_price"] - product["new_price"]) / product[
            "original_price"]) * 100

        product_obj = await Product.create(**product, business=user)
        product_obj = await product_pydantic.from_tortoise_orm(product_obj)

        return {"status": "successful", "data": product_obj}

    return {"status": "error"}


@router.get("/product")
async def get_products():
    response = await product_pydantic.from_queryset(Product.all())
    return {"status": "successful", "data": response}


@router.get("/product/{id}")
async def get_product(id: int):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner
    response = await product_pydantic.from_queryset_single(Product.get(id=id))

    return {
        "status": "successful",
        "data": {
            "product_details": response,
            "business_details": {
                "name": business.business_name,
                "city": business.city,
                "region": business.region,
                "description": business.business_description,
                "logo": business.logo,
                "owner_id": owner.id,
                "business_id": business.id,
                "owner_email": owner.email,
                "join_date": owner.join_date.strftime("%d %b &Y")
            }
        }
    }


@router.delete("/product/{id}")
async def delete_product(id: int, user: user_pydantic = Depends(get_current_user)):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner

    if user == owner:
        await product.delete()

    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return {"status": "successful"}


@router.put("/product/{id}")
async def update_product(
        id: int, update_info: product_pydanticIn, user: user_pydantic = Depends(get_current_user)
):
    product = await Product.get(id=id)
    business = await product.business
    owner = await business.owner

    update_info = update_info.dict(exclude_unset=True)
    update_info["date_published"] = datetime.utcnow()

    if user == owner and update_info["original_price"] > 0:
        update_info["percentage_discount"] = ((update_info["original_price"] - update_info["new_price"]) / update_info[
            "original_price"]) * 100

        await product.update_from_dict(update_info)
        response = await product_pydantic.from_tortoise_orm(product)
        return {"status": "successful", "data": response}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password",
        headers={"WWW-Authenticate": "Bearer"}
    )
