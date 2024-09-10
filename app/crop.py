import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import os

class ImageCropper:
    def __init__(self, model, target_size=(224, 224)):
        self.model = model
        self.target_size = target_size

    def load_image(self, image_path):
        image = Image.open(image_path).convert("RGB")
        original_size = image.size
        return image, original_size

    def resize_image(self, image):
        image = image.resize(self.target_size)
        image = np.array(image) / 255.0  
        image = np.expand_dims(image, axis=0)  
        return image

    def load_and_resize_image(self, image_path):
        image, original_size = self.load_image(image_path)
        resized_image = self.resize_image(image)
        return resized_image, original_size

    def predict_bounding_box(self, resized_image):
        predictions = self.model.predict(resized_image)
        bbox = predictions[0]
        return bbox

    def map_bboxes_to_original_size(self, bbox, original_size):
        scale_x = original_size[0] / self.target_size[0]
        scale_y = original_size[1] / self.target_size[1]
        xmin, ymin, h, w = bbox
        original_bbox = [xmin * scale_x, ymin * scale_y, w * scale_x, h * scale_y]
        return original_bbox
    
    def crop_image(self, image_path, bbox):
        image = Image.open(image_path).convert("RGB")
        xmin, ymin, w, h = map(int, bbox)
        xmax = xmin + w
        ymax = ymin + h
        cropped_image = image.crop((xmin, ymin, xmax, ymax))
        return cropped_image

    def process_image(self, image_path):
        resized_image, original_size = self.load_and_resize_image(image_path)
        bbox = self.predict_bounding_box(resized_image)
        original_bbox = self.map_bboxes_to_original_size(bbox, original_size)
        cropped_image = self.crop_image(image_path, original_bbox)
        return cropped_image
    
    def save_cropped_images(self, cropped_images, output_dir):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for i, cropped_image in enumerate(cropped_images):
            save_path = os.path.join(output_dir, f'cropped_image_{i+1}.jpg')
            cropped_image.save(save_path)

