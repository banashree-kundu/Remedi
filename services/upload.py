from imagekitio import ImageKit
import requests
import os
import base64
# Configuration
imagekit = ImageKit(private_key=os.environ.get('IMAGEKIT_PRIVATE_KEY'),public_key=os.environ.get('IMAGEKIT_PUBLIC_KEY'),url_endpoint=os.environ.get('IMAGEKIT_URL_ENDPOINT'))
def upload_document(file, file_name):
     try:
        
        print(f"Uploading file: {file_name}")
        # 1. Read file bytes
        file.seek(0)
        file_bytes = file.read()

        encoded_string = base64.b64encode(file_bytes).decode('utf-8')
        upload = imagekit.upload_file(
            file=encoded_string,                 # ✅ pass object/bytes directly
            file_name=file_name
        )
        # 3. Handle the response safely
        # Some versions return an object, others a dict. We check both.
        if hasattr(upload, 'url'):
            print(f"Upload Success (Object): {upload.url}")
            return upload.url
        elif isinstance(upload, dict) and 'url' in upload:
            print(f"Upload Success (Dict): {upload['url']}")
            return upload['url']
        elif hasattr(upload, 'response_metadata'): 
            # Fallback for newer SDK versions if .url attribute is missing directly
            return upload.response_metadata.get('raw', {}).get('url')
        else:
            print(f"Unknown response format: {upload}")
            return None

     except Exception as e:
        print(f"Error uploading document: {e}")
        return None

