from pydantic import BaseSettings

class Settings(BaseSettings):
    secret: str
    sendgrid_api_key: str


    class Config:
        env_file = "../.env"


settings = Settings()