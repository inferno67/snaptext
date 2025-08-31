# 🖼️ SnapText OCR Tool

Extract text from screenshots and images using **OCR (Optical Character Recognition)** in Python.  
Supports both **terminal** and **drag & drop GUI** versions.

---

## 🚀 Features
- Extract text from any image
- Supports `.png`, `.jpg`, `.jpeg`, `.bmp`
- Lightweight & beginner-friendly
- Drag & drop GUI for easy use
- Save extracted text to `.txt`

---

## 📦 Installation

1. Clone this repo:
```bash
git clone https://github.com/your-username/snaptext.git
cd snaptext
```

2. Install Python dependencies:
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

4. (Windows only) Set Tesseract path in `ocr_tool.py` or `ocr_gui.py` if needed:
```python
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

---

## ▶️ Usage

### Terminal Version
```bash
python ocr_tool.py example.png
```
- Output is printed in the terminal.

### GUI Version
```bash
python ocr_gui.py
```
- GUI window opens.
- Click **Select Image** → choose an image.  
- OCR text appears in the box.  
- Click **Save Text as .txt** to save output.

---
