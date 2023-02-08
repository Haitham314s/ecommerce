from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from routers import businesses, products, users
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(users.router)
app.include_router(products.router)
app.include_router(businesses.router)

app.mount('/users', users.app)
app.mount('/products', products.app)

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
