from fastapi.exceptions import HTTPException
from passlib.context import CryptContext
import jwt
from dotenv import dotenv_values
from .models import User
from fastapi import status


config_credentials = dotenv_values(".env")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_hashed_password(password):
    return pwd_context.hash(password)


def verify_token(token:str):
    try:
        payload = jwt.decode(token, config_credentials["SECRET"])
        user = await User.get(id=payload.get("id"))

    except:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"}
        )

    return user
