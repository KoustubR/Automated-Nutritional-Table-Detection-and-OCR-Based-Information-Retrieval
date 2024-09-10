from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import io
import os
import pandas as pd
from tempfile import NamedTemporaryFile
from crop import ImageCropper
from tensorflow.keras.models import load_model
from iou_loss import IoULoss
from utils import download_image_from_gcs, extract_text_from_image, extract_nutrition_info_per_serving
import logging
from google.cloud import storage

app = FastAPI()

model = load_model('/app/models/resnet_tuned_model.h5', custom_objects={'IoULoss': IoULoss})
image_cropper = ImageCropper(model)

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

@app.post("/extract_nutrients/")
async def extract_nutrients(file: UploadFile = File(...)):
    logger.info("Extract nutrients endpoint called.")
    
    with NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        logger.info("Saving uploaded file to a temporary location.")
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        logger.info("Cropping the image.")
        cropped_image = image_cropper.process_image(temp_file_path)
        logger.info("Uploading cropped image to Google Cloud Storage.")
        storage_client = storage.Client()
        bucket_name = os.getenv("GCS_BUCKET_NAME")
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(f"cropped_images/{os.path.basename(temp_file_path)}")
        cropped_image_bytes = io.BytesIO()
        cropped_image.save(cropped_image_bytes, format="JPEG")
        blob.upload_from_string(cropped_image_bytes.getvalue(), content_type="image/jpeg")
        
        logger.info("Downloading cropped image from GCS for text extraction.")
        image_data = download_image_from_gcs(bucket_name, f"cropped_images/{os.path.basename(temp_file_path)}")
        extracted_text = extract_text_from_image(image_data)
        
        if extracted_text:
            try:
                logger.info("Extracting nutritional information from OCR results.")
                nutritional_info = extract_nutrition_info_per_serving(extracted_text)

                filtered_nutritional_info = {key: value for key, value in nutritional_info.items() if value}
                df = pd.DataFrame(list(filtered_nutritional_info.items()), columns=['Nutrient', 'Amount'])

                logger.info("Returning formatted nutrients as JSON.")
                return df.to_json(orient='records')

            except Exception as e:
                logger.error(f"Error during nutrition info extraction: {e}")
                return JSONResponse(content={"error": f"Error during nutrition info extraction: {e}"}, status_code=500)
        else:
            logger.error("No text extracted from the image.")
            return JSONResponse(content={"error": "No text extracted from the image."}, status_code=400)
    
    finally:
        logger.info(f"Removing temporary file: {temp_file_path}.")
        os.remove(temp_file_path)

@app.post("/crop/")
async def crop_image(file: UploadFile = File(...)):
    logger.info("Cropping image endpoint called.")
    
    with NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(await file.read())
        temp_file_path = temp_file.name

    try:
        logger.info("Processing image crop.")
        cropped_image = image_cropper.process_image(temp_file_path)
        cropped_image_bytes = io.BytesIO()
        cropped_image.save(cropped_image_bytes, format="JPEG")
        cropped_image_bytes.seek(0)

        logger.info("Returning cropped image as a streaming response.")
        return StreamingResponse(cropped_image_bytes, media_type="image/jpeg")
    
    finally:
        logger.info(f"Removing temporary file: {temp_file_path}.")
        os.remove(temp_file_path)

@app.get("/health")
def health_check():
    logger.info("Health check called.")
    return {"status": "healthy"}

app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")
