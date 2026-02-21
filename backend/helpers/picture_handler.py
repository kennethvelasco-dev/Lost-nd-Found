import os
import uuid
from werkzeug.utils import secure_filename
from backend.models import ValidationError

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
MAX_UPLOAD_SIZE = 5 * 1024 * 1024  # 5 MB

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_picture_size(file_content: bytes):
    if len(file_content) > MAX_UPLOAD_SIZE:
        raise ValidationError("File size exceeds 5MB limit", 400)
    return True

def save_picture(file_storage, upload_folder='static/uploads'):
    """
    Saves a Flask FileStorage object locally and returns the relative URL.
    """
    if not file_storage or not file_storage.filename:
        return None
        
    if not allowed_file(file_storage.filename):
        raise ValidationError("Invalid file type. Allowed: png, jpg, jpeg, webp", 400)
        
    # Read content to check size, then reset pointer
    file_content = file_storage.read()
    validate_picture_size(file_content)
    file_storage.seek(0)
    
    os.makedirs(upload_folder, exist_ok=True)
    
    # Generate unique filename
    ext = file_storage.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"{uuid.uuid4().hex}.{ext}"
    
    file_path = os.path.join(upload_folder, unique_filename)
    file_storage.save(file_path)
    
    return f"/{upload_folder}/{unique_filename}"
