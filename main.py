import jwt
from fastapi import FastAPI, HTTPException, status, Depends
from tortoise.contrib.fastapi import register_tortoise
from models.business import *
from models.user import *
from models.product import *
from dotenv import dotenv_values
from routers import businesses, users, products
# Authentication

config_credentials = dotenv_values(".env")

app = FastAPI()

app.include_router(users.router)
app.include_router(products.router)
app.include_router(businesses.router)


@app.get("/")
async def index():
    return {"details": "Not found"}


register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models.user", "models.product", "models.business"]},
    generate_schemas=True,
    add_exception_handlers=True
)
