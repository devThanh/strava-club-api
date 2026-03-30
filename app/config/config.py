import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_USER = os.getenv("DATABASE_USERNAME")
    DB_PASSWORD = os.getenv("DATABASE_PASSWORD")
    DB_HOST = os.getenv("DATABASE_HOST")
    DB_PORT = os.getenv("DATABASE_PORT")
    DB_NAME = os.getenv("DATABASE_NAME")
    IS_PRODUCT = os.getenv("IS_PRODUCTION")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM")
    ACCESS_TOKEN_EXPIRE_MINUTES = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
    REFRESH_TOKEN_EXPIRE_DAYS = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
    IMAGEKIT_PRIVATE_KEY=os.getenv("IMAGEKIT_PRIVATE_KEY")
    IMAGEKIT_PUBLIC_KEY=os.getenv("IMAGEKIT_PUBLIC_KEY")
    IMAGEKIT_URL=os.getenv("IMAGEKIT_URL")
    OCR_API_KEY=os.getenv("OCR_API_KEY")

config = Config()
