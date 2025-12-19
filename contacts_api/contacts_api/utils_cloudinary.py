import cloudinary
import cloudinary.uploader
from .config import CLOUDINARY_CLOUD_NAME, CLOUDINARY_API_KEY, CLOUDINARY_API_SECRET

if CLOUDINARY_CLOUD_NAME:
    cloudinary.config(
        cloud_name=CLOUDINARY_CLOUD_NAME,
        api_key=CLOUDINARY_API_KEY,
        api_secret=CLOUDINARY_API_SECRET,
    )

def upload_avatar(file_bytes, filename):
    res = cloudinary.uploader.upload(file_bytes, public_id=filename, overwrite=True)
    return res.get("secure_url")
