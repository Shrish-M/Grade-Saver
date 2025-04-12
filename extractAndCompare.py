import cv2
import numpy as np
import pytesseract

#image - extract image hardcoded for now




#clean - reduce noise, object detection (annotations), maybe OCR if applicable
img = cv2.imread('./Test-Page.jpg')

resized_img = cv2.resize(img, (400, 600), interpolation=cv2.INTER_AREA)

if img is None:
    print('No image')

window_name = 'My Image Display'

cv2.imshow(window_name, resized_img)
cv2.waitKey(0)



img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

resized_img = cv2.resize(img_gray, (400, 600), interpolation=cv2.INTER_AREA)


cv2.imshow(window_name, resized_img)
cv2.waitKey(0)

kernel = np.ones((3,3),np.uint8)
denoised = cv2.GaussianBlur(img_gray, (1,1), 0)

resized_img = cv2.resize(denoised, (400, 600), interpolation=cv2.INTER_AREA)
cv2.imshow(window_name, resized_img)
cv2.waitKey(0)


_, thresh = cv2.threshold(denoised, 245, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
resized_img = cv2.resize(thresh, (400, 600), interpolation=cv2.INTER_AREA)
cv2.imshow(window_name, resized_img)
cv2.waitKey(0)

_, thresh = cv2.threshold(img_gray, 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
resized_img = cv2.resize(thresh, (400, 600), interpolation=cv2.INTER_AREA)
cv2.imshow(window_name, resized_img)
cv2.waitKey(0)

_, thresh = cv2.threshold(img_gray, 125, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
resized_img = cv2.resize(thresh, (400, 600), interpolation=cv2.INTER_AREA)
cv2.imshow(window_name, resized_img)
cv2.waitKey(0)

cv2.destroyAllWindows()

text = pytesseract.image_to_string(denoised)  # skip threshold entirely
print(text)
#compare rubric

#call function to get rubric and points deductions



#general-response from a multimodal LLM that can anaylze our image



