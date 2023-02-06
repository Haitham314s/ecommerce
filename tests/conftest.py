import pytest
from tortoise import Tortoise, run_async
import jwt
from fastapi import Depends, HTTPException
from fastapi.testclient import TestClient

from auth import get_hashed_password, verify_password, token_generator, oauth2_schema
from models.user import User, user_pydantic, user_pydanticIn
from main import app

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"


@pytest.fixture(scope="session", autouse=True)
def setup_db():
    async def _init_db():
        await Tortoise.init(
            db_url='sqlite://:memory:',
            modules={'models': ['models']}
        )
        await Tortoise.generate_schemas()

    run_async(_init_db)


@pytest.fixture(autouse=True)
async def clear_db():
    await Tortoise.close_connections()
    for name, adapter in Tortoise._connections.items():
        adapter.drop_all_tables()


async def user_registrations(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    user_info["password"] = get_hashed_password(user_info["password"])
    user_obj = await User.create(**user_info)
    new_user = await user_pydantic.from_tortoise_orm(user_obj)
    return {
        "status": "ok",
        "user": new_user
    }


async def user_login(user: user_pydanticIn):
    user_info = user.dict(exclude_unset=True)
    stored_user = await User.get(email=user_info["email"])
    if not stored_user:
        raise HTTPException(status_code=400, detail="Email not found")
    if not verify_password(user_info["password"], stored_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")
    access_token = token_generator(data={"user_id": stored_user.id, "email": stored_user.email})
    return {
        "status": "ok",
        "access_token": access_token,
        "user_id": stored_user.id,
        "email": stored_user.email,
    }


def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=400, detail="Could not validate credentials"
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id", None)
        if user_id is None:
            raise credentials_exception
        user = User.get(id=user_id)
        if user is None:
            raise credentials_exception
        return user
    except (jwt.PyJWTError, Exception):
        raise credentials_exception


@pytest.fixture
def authenticated_user(client):
    email = "test@example.com"
    password = "secret-password"

    # Register the user
    response = client.post("/registration", json={"email": email, "password": password})
    assert response.status_code == 200

    # Log in the user
    response = client.post("/login", json={"email": email, "password": password})
    assert response.status_code == 200
    return response.json()["access_token"]


@pytest.fixture
def client():
    return TestClient(app)
