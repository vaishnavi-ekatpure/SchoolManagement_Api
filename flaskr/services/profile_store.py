import base64
import os
from io import BytesIO
from PIL import Image
import uuid

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def ensure_upload_folder_exists(upload_folder_path):
    if not os.path.exists(upload_folder_path):
        os.makedirs(upload_folder_path)

def upload_profile_image(base64_image, upload_folder_path):

    ensure_upload_folder_exists(upload_folder_path)

    if not base64_image.startswith('data:image/'):
        return {'error': 'Invalid base64 image format', 'flage': False}

    image_data = base64_image.split(',')[1]

    try:
        image_data = base64.b64decode(image_data)

        image = Image.open(BytesIO(image_data))

        if image.format.lower() not in ALLOWED_EXTENSIONS:
            return ({'error': 'Invalid image format. Allowed formats are png, jpg, jpeg.', 'flage': False})

        image_filename = f"{uuid.uuid4().hex}.{image.format.lower()}"

        image.save(os.path.join(upload_folder_path, image_filename))
        return {'flage': True, 'filename': image_filename}

    except Exception as e:
        return {'error': f'Failed to process image: {str(e)}', 'flage': False}
