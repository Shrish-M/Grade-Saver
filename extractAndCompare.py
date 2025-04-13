import cv2
import numpy as np
import pytesseract

#image - extract image hardcoded for now


def show_image(window_name, image):
    cv2.imshow(window_name, image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

def clean_image():
    # clean - reduce noise, object detection (annotations), maybe OCR if applicable
    img = cv2.imread('./Test-Page.jpg')

    resized_img = cv2.resize(img, (400, 600), interpolation=cv2.INTER_AREA)

    if img is None:
        print('No image')

    window_name = 'My Image Display'

    show_image(window_name, resized_img)

    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    _, thresh = cv2.threshold(img_gray, 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    resized_img = cv2.resize(thresh, (400, 600), interpolation=cv2.INTER_AREA)
    show_image("Gray", resized_img)

    clahe = cv2.createCLAHE(clipLimit=0.1, tileGridSize=(
    14, 14))  # larger tiles = more global transformation, low clipLimit reduces unecessary noise
    enhanced = clahe.apply(img_gray)

    resized_img = cv2.resize(thresh, (400, 600), interpolation=cv2.INTER_AREA)
    show_image("Enhanced", resized_img)

    # Assume 'gray' is your grayscale image.
    adaptive_thresh = cv2.adaptiveThreshold(
        enhanced,  # Source image (grayscale)
        255,  # Maximum value assigned to pixel values exceeding the threshold
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,  # Adaptive method using a weighted sum of neighborhood values
        cv2.THRESH_BINARY,  # Threshold type (binary: if pixel value > threshold -> maxValue, else 0)
        21,  # blockSize: Size of the neighborhood area (must be an odd number), larger sizes help smoothen
        2  # Constant (C) subtracted from the computed mean or weighted sum
    )

    resized_img = cv2.resize(adaptive_thresh, (400, 600), interpolation=cv2.INTER_AREA)
    show_image(window_name, resized_img)
    return adaptive_thresh

clean_image()



#text
#compare rubric

#call function to get rubric and points deductions



#general-response from a multimodal LLM that can anaylze our image



