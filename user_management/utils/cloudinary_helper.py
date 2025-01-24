import cloudinary.uploader

def upload_to_cloudinary(file):
    """
    Upload a file to Cloudinary and return the secure URL.

    Returns:
    - The secure URL of the uploaded file, or None if the upload fails.
    """
    if not file:
        print("No file provided for upload.")  
        return None  

    try:
        # Perform the file upload
        upload_result = cloudinary.uploader.upload(file)
        return upload_result.get('secure_url')  # Return the secure URL of the uploaded file
    except Exception as e:
        # Print the error message and return None
        print(f"Error uploading file to Cloudinary: {e}")
        return None



def handle_multiple_uploads(files_dict):
    """
    Upload multiple files using a single function call.

    Returns:
    - A dictionary with the same keys and Cloudinary secure URLs as values (or None if upload failed).
    """
    # Using a dictionary comprehension to simplify file upload
    return {key: upload_to_cloudinary(file) for key, file in files_dict.items() if file}
