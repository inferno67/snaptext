import cv2
import pytesseract
from PIL import Image
import sys
import os

# If using Windows, set path to Tesseract manually if needed:
# Example: pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def image_to_text(image_path):
    """Extract text from image file"""
    if not os.path.exists(image_path):
        print("❌ File not found:", image_path)
        return None

    # Load image with OpenCV
    img = cv2.imread(image_path)

    if img is None:
        print("❌ Unable to load image:", image_path)
        return None

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Apply thresholding (helps improve OCR results)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    # Save temporary file for Tesseract
    temp_filename = "temp.png"
    cv2.imwrite(temp_filename, thresh)

    # Extract text using Tesseract
    text = pytesseract.image_to_string(Image.open(temp_filename))

    # Delete temp file
    os.remove(temp_filename)

    return text.strip()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python ocr_tool.py <image_path>")
        sys.exit(1)

    image_path = sys.argv[1]
    extracted_text = image_to_text(image_path)

    if extracted_text:
        print("\n📄 Extracted Text:\n")
        print(extracted_text)
    else:
        print("⚠️ No text detected.")
# To check OpenCV version, run these lines in a Python shell:
# import cv2
# print(cv2.__version__)
