# 🖼️ SnapText OCR Tool

Extract text from screenshots and images using **OCR (Optical Character Recognition)** in Python.  
Supports both **terminal** and **drag & drop GUI** versions with **enhanced text extraction**.

---

## 🚀 Features
- Extract text from any image (single or multiple images)
- Drag & drop support in GUI
- Enhanced OCR accuracy using:
  - Grayscale + CLAHE contrast enhancement
  - Sharpening & noise removal
  - Adaptive thresholding & dilation
  - PSM 6 mode for full-block recognition
- Multi-language OCR support (English, Hindi, Spanish, French, German)
- Save extracted text to `.txt` or `.pdf`
- Lightweight & beginner-friendly GUI
- Dark mode GUI with white buttons for readability

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

- Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki
- Linux: sudo apt install tesseract-ocr
- macOS (Homebrew): brew install tesseract

4. (Windows only) Set Tesseract path in `ocr_gui.py` if needed:
```bash
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
- Select **language** from dropdown (optional).
- Click **Select Images** → choose one or multiple images.
- Drag & drop images directly into the text box (if `tkinterdnd2` installed).
- OCR text appears in the box.
- Click **Save Text as .txt** or **Save as .pdf** to save output.

---

## ⚡ Notes
- Make sure Tesseract is installed and correctly added to your system PATH.
- For best results, use high-resolution images.
- Multi-language OCR requires the corresponding Tesseract language files.
