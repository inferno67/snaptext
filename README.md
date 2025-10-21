# 🖼️ SnapText Ultimate OCR Tool

Extract text from screenshots and images using **OCR (Optical Character Recognition)**.  
Supports both **terminal**, **GUI**, and **standalone Windows app** versions with **enhanced text extraction**.

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

## 📦 Installation (Python version)

### 1️⃣ Clone this repo
```bash
git clone https://github.com/inferno67/snaptext.git
cd snaptext
```
2️⃣ Install Python dependencies
```bash
pip install pillow pytesseract opencv-python fpdf numpy pyperclip tkinterdnd2 mss keyboard
```
3️⃣ Install Tesseract OCR

Windows:

 Download from [UB Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)

Linux:

```bash
sudo apt install tesseract-ocr
```
macOS (Homebrew):

```bash
brew install tesseract
```
Windows only (if Tesseract is not in PATH):

python
```bash
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
```

▶️ Usage (Python version)

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

Real-time screenshot OCR → click Screenshot OCR.

Partial screen OCR → click Partial OCR.

Hotkey screenshot OCR → press Ctrl+Shift+S.

🖥️ Usage (Standalone Windows App)

If you don’t want to install Python or dependencies, download the SnapText.exe from the Releases section.

Download SnapText.exe from the latest release.

Place it anywhere you like (Desktop, Documents, etc.).

Open a terminal or PowerShell and navigate to the dist folder:
```bash
cd path\to\SnapText\dist
.\SnapText.exe
```

Double-clicking SnapText.exe in dist/ also works.

All GUI features work exactly like the Python version.

For Tesseract OCR to work, make sure Tesseract is installed and in PATH (or follow the embedded instructions for Windows).

⚡ Notes
Make sure Tesseract is installed and correctly added to your system PATH.

For best results, use high-resolution images.

Multi-language OCR requires the corresponding Tesseract language files.

Preprocessing options (Grayscale, CLAHE, Noise Removal, Sharpening, Adaptive Thresholding) can be customized and saved as presets.

The standalone .exe version works on Windows without Python, but still requires Tesseract OCR for text extraction.

📬 Contact Me

[Join my Discord server](https://discord.gg/SqyFzxZdjH)

iaminferno@gmail.com