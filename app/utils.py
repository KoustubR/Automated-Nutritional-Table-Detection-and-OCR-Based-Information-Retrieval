from google.cloud import storage, vision

def download_image_from_gcs(bucket_name, gcs_blob_name):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_blob_name)
    image_data = blob.download_as_bytes()
    return image_data

def extract_text_from_image(image_data):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_data)
    
    response = client.text_detection(image=image)
    texts = response.text_annotations
    
    if texts:
        extracted_text = texts[0].description
        return extracted_text
    else:
        return None

def extract_nutrition_info_per_serving(ocr_results):
    nutrition_info = {}
    ocr_results = ocr_results.splitlines()
    for i, text in enumerate(ocr_results):
        if "Energy" in text:
            nutrition_info['Energy'] = ocr_results[i + 1]
        elif "Fat" in text and "saturates" not in ocr_results[i + 1]:
            nutrition_info['Fat'] = ocr_results[i + 1]
        elif "saturates" in text:
            nutrition_info['Saturates'] = ocr_results[i + 1]
        elif "Carbohydrate" in text:
            nutrition_info['Carbohydrate'] = ocr_results[i + 1]
        elif "sugars" in text:
            nutrition_info['Sugars'] = ocr_results[i + 1]
        elif "Fibre" in text:
            nutrition_info['Fibre'] = ocr_results[i + 1]
        elif "Protein" in text:
            nutrition_info['Protein'] = ocr_results[i + 1]
        elif "Salt" in text:
            nutrition_info['Salt'] = ocr_results[i + 1]
    
    return nutrition_info
