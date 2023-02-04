import jwt
from fastapi import FastAPI, Request, HTTPException, status, Depends
from tortoise.contrib.fastapi import register_tortoise
from models import *
from dotenv import dotenv_values

# Authentication
from auth import get_hashed_password, verify_token, token_generator
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# Signals
from tortoise.signals import post_save
from typing import List, Optional, Type
from tortoise import BaseDBAsyncClient
from emails import send_email

# Response classes
from fastapi.responses import HTMLResponse

# Templates
from fastapi.templating import Jinja2Templates

# Images
from fastapi import File, UploadFile
import secrets
from fastapi.staticfiles import StaticFiles
from PIL import Image

config_credentials = dotenv_values(".env")

app = FastAPI()

# Static file setup configuration
app.mount("/staic", StaticFiles(directory="static"), name="static")

oauth2_schema = OAuth2PasswordBearer(tokenUrl="token")


@app.post("/token")
async def generate_token(request_form: OAuth2PasswordRequestForm = Depends()):
    token = await token_generator(request_form.username, request_form.password)
    return {"access_token": token, "token_type": "bearer"}


async def get_current_user(token: str = Depends(oauth2_schema)):
    try:
        payload = jwt.decode(token, config_credentials["SECRET"], algorithms=["HS256"])
        user = await User.get(id=payload.get("id"))

    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return await user


@app.post("/user/me")
async def user_login(user: user_pydanticIn = Depends(get_current_user)):
    business = await Business.get(owner=user)

    return {
        "status": "ok",
        "data": {
            "username": user.username,
            "email": user.email,
            "verified": user.is_verified,
            "joined_date": user.join_date.strftime("%b/%d/%Y")
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
        # TODO: Send the email
        await send_email([instance.email], instance)


@app.post("/registration")
async def user_registrations(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "status": "ok",
        "data": f"Hello {new_user.username} , thanks for choosing our services. Please check your email inbox and "
                f"click on the link to confirm your registration."
    }


templates = Jinja2Templates(directory="templates")


@app.get("/verification", response_class=HTMLResponse)
async def email_verification(request: Request, token: str):
    user = await verify_token(token)

    if user and not user.is_verified:
        user.is_verified = True
        await user.save()
        return templates.TemplateResponse(
            "verification.html",
            {
                "request": request,
                "username": user.username
            })

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid token or expired token",
        headers={"WWW-Authenticate": "Bearer"}
    )


@app.get("/")
async def index():
    return {"details": "Not found"}


@app.post("/upload_file/profile")
async def create_profile_file(
        file: UploadFile = File(...),
        user: user_pydantic = Depends(get_current_user)
):
    filename = file.filename
    # Test.png
    extension = filename.split(".")[1]

    if extension not in ["png", "jpg"]:
        return {"status": "error", "detail": "File extension not supported"}

    token_name = f"{secrets.token_hex(10)}.{extension}"
    generated_name = f"./static/images/{token_name}"
    file_content = await file.read()

    with open(generated_name, "wb") as file:
        file.write(file_content)

    # PILLOW
    img = Image.open(generated_name)
    img = img.resize(size=(200, 200))
    img.save(generated_name)

    file.close()

    business = await Business.get(owner=user)
    owner = await business.owner

    if owner != user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated to perform this action",
            headers={"WWW-Authenticate": "Bearer"}
        )
    business.logo = token_name
    await business.save()

    file_url = f"localhost:9000{generated_name[1:]}"

    return {"status": "successful", "filename": file_url}


@app.post("/upload_file/product/{id}")
async def create_product_file(
        id: int,
        file: UploadFile = File(...),
        user: user_pydantic = Depends
):
    filename = file.filename
    # Test.png
    extension = filename.split(".")[1]

    if extension not in ["png", "jpg"]:
        return {"status": "error", "detail": "File extension not supported"}

    token_name = f"{secrets.token_hex(10)}.{extension}"
    generated_name = f"./static/images/{token_name}"
    file_content = await file.read()

    with open(generated_name, "wb") as file:
        file.write(file_content)

    # PILLOW
    img = Image.open(generated_name)
    img = img.resize(size=(200, 200))
    img.save(generated_name)

    file.close()

    product = await Product.get(id=id)
    business = await product.business
    owner = business.owner

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


register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
