# 🖼️ Screenshot to Text (OCR Tool)

A simple Python tool that extracts text from images (screenshots, documents, photos) using **OCR (Tesseract)**.

---

## 🚀 Features
- Extract text from any image
- Supports `.png`, `.jpg`, `.jpeg`, and more
- Lightweight & beginner-friendly

---

## 📦 Installation

1. Clone this repo:
```bash
git clone https://github.com/your-username/ocr-tool.git
cd ocr-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install **Tesseract OCR**:
- [Windows Download](https://github.com/UB-Mannheim/tesseract/wiki)
- Linux:
```bash
sudo apt install tesseract-ocr
```
- macOS (Homebrew):
```bash
brew install tesseract
```

4. (Windows only) Set the Tesseract path in `ocr_tool.py` if needed:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## ▶️ Usage

Run the script with an image file:
```bash
python ocr_tool.py example.png
```

Output:
```
📄 Extracted Text:

Hello, this text came from an image!
```