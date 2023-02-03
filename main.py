from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from models import *

app = FastAPI()


@app.get("/")
async def index():
    return {"details": "Not found"}


register_tortoise(
    app,
    db_url="sqlite://database.sqlite3",
    modules={"models": ["models"]},
    generate_schemas=True,
    add_exception_handlers=True
)
