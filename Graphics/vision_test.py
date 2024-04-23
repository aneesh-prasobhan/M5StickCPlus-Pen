#vision_test.py
import os
from google.cloud import vision_v1 as vision
from google.cloud.vision_v1 import AnnotateImageRequest
from PIL import Image
from io import BytesIO
import pygame
from google.cloud.vision_v1 import ImageContext
import json
import base64


# Your list of coordinates
coordinates = []


def build_request_json(request):
    json_request = {
        "image": {
            "content": "image"
        },
        "features": [{"type": feature.type} for feature in request.features],
    }

    if request.image_context:
        # Convert the repeated field to a list for serialization
        language_hints = [hint for hint in request.image_context.language_hints]
        json_request["imageContext"] = {
            "languageHints": language_hints
        }

    return json_request

# # Function to create image from coordinates
# def create_image_from_coordinates(coordinates, image_size=(300, 300), line_width=10):
#     image = Image.new("RGB", image_size, "white")
#     draw = ImageDraw.Draw(image)
#     draw.line(coordinates, fill="black", width=line_width)
#     return image

def process_image(image_surface, language=None):
    # Save the pygame.Surface object to a file
    pygame.image.save_extended(image_surface, "temp_image.jpg")

    # Open the saved image file
    image = Image.open("temp_image.jpg")
    
    # Google Cloud Vision API setup
    current_directory = os.path.dirname(os.path.abspath(__file__))
    credentials_file_path = os.path.join(current_directory, 'academic-arcade-386319-1032d69b7cc4.json')
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file_path
    client = vision.ImageAnnotatorClient()
    request = AnnotateImageRequest()

    # Convert the image object to a byte array
    image_byte_array = BytesIO()
    image.save(image_byte_array, format="JPEG")
    image_byte_array = image_byte_array.getvalue()

    # Set the image source
    request.image.content = image_byte_array

    # Set the feature type to TEXT_DETECTION
    feature = vision.Feature(type=vision.Feature.Type.TEXT_DETECTION)
    request.features.append(feature)

    # Set the language hint if provided
    if language:
        image_context = ImageContext(language_hints=[language])
        request.image_context = image_context
        print(f"Using language hint: {language}")
        print("Sending to Vision API.")

    
    # print("Sending to API.")
    
    # Rebuilding how the Json looks like (not needed)
    # request_json = build_request_json(request)
    # print(json.dumps(request_json, indent=4))
    
    
    # Send the request to the API
    response = client.annotate_image(request)

    # Iterate through the response
    for r in response.text_annotations:
        d = {
            'text': r.description
        }
        print(d)

    # Remove the temporary image file
    os.remove("temp_image.jpg")