# 🖼️ SnapText Ultimate OCR Tool

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
- Auto-copy OCR text to clipboard (optional)
- OCR History to track previous extractions
- Real-time screenshot OCR
- Partial screen OCR
- Hotkey screenshot OCR (`Ctrl+Shift+S`)

---

## 📦 Installation

1. Clone this repo:
```bash
git clone https://github.com/your-username/snaptext.git
cd snaptext
```
Install Python dependencies:

```bash
pip install pillow pytesseract opencv-python fpdf numpy pyperclip tkinterdnd2 mss keyboard
```
Install Tesseract OCR:

Windows: Download from https://github.com/UB-Mannheim/tesseract/wiki

Linux:
```bash
sudo apt install tesseract-ocr
```
macOS (Homebrew):
```bash
brew install tesseract
```
(Windows only) Set Tesseract path in ocr_gui.py if needed:
```bash
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```
▶️ Usage
Terminal Version
```bash
python ocr_tool.py example.png
```
Output is printed in the terminal.

GUI Version
```bash
python ocr_gui.py
```
GUI window opens.

Select language(s) from the checkboxes.

Click Select Images → choose one or multiple images.

Drag & drop images directly into the text box (if tkinterdnd2 installed).

OCR text appears in the box.

Save Text as .txt or .pdf.

Auto-copy feature copies text to clipboard automatically (if pyperclip installed).

Real time screenshot OCR → click Screenshot OCR.

Partial screen OCR → click Partial OCR.

Hotkey screenshot OCR → press Ctrl+Shift+S.

# ⚡ Notes
Make sure Tesseract is installed and correctly added to your system PATH.

For best results, use high-resolution images.

Multi-language OCR requires the corresponding Tesseract language files.

Preprocessing options (Grayscale, CLAHE, Noise Removal, Sharpening, Adaptive Thresholding) can be customized and saved as presets.