from dotenv import load_dotenv
from imagekitio import ImageKit
import os

from app.config.config import config

load_dotenv()


imagekit = ImageKit(
    private_key=config.IMAGEKIT_PRIVATE_KEY,
    # public_key= os.getenv("IMAGEKIT_PUBLIC_KEY"),
    # url_endpoint=os.getenv("IMAGEKIT_URL"),
)