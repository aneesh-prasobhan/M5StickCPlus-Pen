
* * *

M5StickC-Plus Digital Pen
=========================

Overview
--------

The M5StickC-Plus Digital Pen is an innovative project that leverages the 6-Axis IMU of the M5Stick C Plus to track its orientation in space. This enables users to convert their physical pen movements into digital images. These images are then sent to the Google Vision API for handwriting recognition.

Firmware
--------

The firmware for the M5StickC-Plus is located in the `src` and `include` folders of this repository.

BoardDisplay\_naive.py
----------------------

To interface with the M5StickC-Plus Pen, run the `BoardDisplay_naive.py` script on a PC connected to the device. This script will display the orientation of the pen in real-time.
Press the button and start writing the word, after you're done, this word should be displayed as an image first. Then the google vision api will send the detected text from the image.

Setup Instructions
------------------

### Pre-requisites

1.  **Connect the M5StickC-Plus Device**: Ensure that the M5StickC-Plus device, loaded with the appropriate firmware, is connected to your laptop.
    
2.  **Google Vision API Setup**:
    
    *   **Google Cloud Console Access**: Navigate to the Google Cloud Console to create an API credentials JSON file.
    *   **Create a Service Account**: In the GCP console, go to "IAM & Admin" > "Service accounts". Create a new service account and assign it the necessary roles. For the Vision API, roles like "Viewer" or specific Vision API roles are recommended.
    *   **Create and Download Key**: Generate a key for the service account and download it in JSON format. This will be the `academic-arcade-386319-1032d69b7cc4.json` file referenced in the `vision_test.py` code.
    *   **Using the Key**: Place this JSON file in the `Graphics` folder. Update the file path in the `vision_test.py` script as follows:
        
        luaCopy code
        
        `# Google Cloud Vision API setup current_directory = os.path.dirname(os.path.abspath(__file__)) credentials_file_path = os.path.join(current_directory, 'academic-arcade-386319-1032d69b7cc4.json') os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file_path client = vision.ImageAnnotatorClient() request = AnnotateImageRequest()`
        
### Requirements
* python 3.8.10
* numpy
* pygame
* pyserial
* pandas
* google-cloud-vision
* pillow

Contribution
------------

Feel free to contribute to the project by submitting pull requests or opening issues for any bugs or feature enhancements.

* * *

_**Created by Aneesh Prasobhan**_

* * *

