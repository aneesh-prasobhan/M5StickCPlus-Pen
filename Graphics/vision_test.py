# import os
# from google.cloud import vision_v1 as vision
# from google.cloud.vision_v1 import AnnotateImageRequest

# # Get the absolute path to the JSON file
# current_directory = os.path.dirname(os.path.abspath(__file__))
# credentials_file_path = os.path.join(current_directory, 'academic-arcade-386319-1032d69b7cc4.json')

# # Set the GOOGLE_APPLICATION_CREDENTIALS environment variable
# os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file_path

# client = vision.ImageAnnotatorClient()

# # Create an AnnotateImageRequest object
# request = AnnotateImageRequest()

# # Get the absolute path to the test image file
# test_image_file_path = os.path.join(current_directory, 'test_image.png')

# # Set the image source
# with open(test_image_file_path, 'rb') as image_file:
#     request.image.content = image_file.read()

# # Set the feature type to TEXT_DETECTION
# feature = vision.Feature(type=vision.Feature.Type.TEXT_DETECTION)
# request.features.append(feature)

# # Send the request to the API
# response = client.annotate_image(request)

# # Iterate through the response
# for r in response.text_annotations:
#     d = {
#         'text': r.description
#     }
#     print(d)


#vision_test.py
import os
from google.cloud import vision_v1 as vision
from google.cloud.vision_v1 import AnnotateImageRequest
from PIL import Image, ImageDraw
from io import BytesIO
import matplotlib.pyplot as plt

# Function to create image from coordinates
def create_image_from_coordinates(coordinates, image_size=(300, 300), line_width=3):
    image = Image.new("RGB", image_size, "white")
    draw = ImageDraw.Draw(image)
    draw.line(coordinates, fill="black", width=line_width)
    return image

# Your list of coordinates
coordinates = [
    (10, 100), (10, 95), (10, 90),(10, 85), (10, 80),(10, 75), (10, 70), (10, 65), (10, 60), (10, 65), (10, 50),  # Vertical line for 'H'
    (10, 75),(15, 75), (20, 75),(25, 75), (30, 75),(35, 75), (40, 75),  # Middle line for 'H'
    (40, 100), (40, 95), (40, 90),(40, 85), (40, 80),(40, 75), (40, 70), (40, 65), (40, 60), (40, 65), (40, 50),  # Vertical line for 'H'
    (60, 100), (70, 100), (80, 100),  # Top line for 'I'
    (60, 50), (70, 50), (80, 50),  # Bottom line for 'I'
    (70, 100), (70, 90), (70, 80), (70, 70), (70, 60), (70, 50),  # Middle vertical line for 'I'
]

# Plot the coordinates
x, y = zip(*coordinates)
plt.scatter(x, y)
plt.show()


# Create an image from the coordinates
image = create_image_from_coordinates(coordinates)

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

# Send the request to the API
response = client.annotate_image(request)

# Iterate through the response
for r in response.text_annotations:
    d = {
        'text': r.description
    }
    print(d)
