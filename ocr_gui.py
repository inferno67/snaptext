import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import pytesseract
import cv2
import os
from fpdf import FPDF  # NEW: for PDF export

# Windows users: set path to Tesseract executable (adjust if installed elsewhere)
# Comment this out on Linux/macOS.
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def run_ocr(image_path):
    """Extract text from image with light preprocessing for better accuracy."""
    if not os.path.exists(image_path):
        return "❌ File not found!"

    img = cv2.imread(image_path)
    if img is None:
        return "❌ Unable to read image!"

    # Basic preprocessing
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Try simple threshold; works well for clean screenshots
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

    temp_file = "temp_snaptext_ocr.png"
    cv2.imwrite(temp_file, thresh)

    try:
        text = pytesseract.image_to_string(Image.open(temp_file))
    except Exception as e:
        text = f"❌ OCR error: {e}"
    finally:
        try:
            os.remove(temp_file)
        except Exception:
            pass

    return text.strip()

def open_file():
    file_path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif")]
    )
    if file_path:
        text = run_ocr(file_path)
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, text)

def save_text():
    text = text_box.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return
    save_path = filedialog.asksaveasfilename(
        title="Save as .txt",
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("Saved", f"Text saved to {save_path}")

def save_pdf():
    """Save the extracted text as a PDF using FPDF."""
    text = text_box.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return

    save_path = filedialog.asksaveasfilename(
        title="Save as .pdf",
        defaultextension=".pdf",
        filetypes=[("PDF files", "*.pdf")]
    )
    if not save_path:
        return

    try:
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        pdf.set_font("Arial", size=12)

        # FPDF (classic) expects latin-1; replace unsupported chars gracefully
        safe_text = text.encode("latin-1", "replace").decode("latin-1")

        # Split into paragraphs and write with multi_cell for wrapping
        for para in safe_text.splitlines():
            if para.strip() == "":
                pdf.ln(5)  # blank line spacing
            else:
                pdf.multi_cell(0, 8, para)

        pdf.output(save_path)
        messagebox.showinfo("Saved", f"PDF saved to {save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create PDF:\n{e}")

# ---- Tkinter GUI ----
root = tk.Tk()
root.title("SnapText – Screenshot OCR")
root.geometry("720x560")

top_bar = tk.Frame(root)
top_bar.pack(pady=10)

btn_open = tk.Button(top_bar, text="Select Image", command=open_file, width=18)
btn_open.grid(row=0, column=0, padx=6)

btn_save_txt = tk.Button(top_bar, text="Save as .txt", command=save_text, width=18)
btn_save_txt.grid(row=0, column=1, padx=6)

# NEW: Save as PDF button
btn_save_pdf = tk.Button(top_bar, text="Save as .pdf", command=save_pdf, width=18)
btn_save_pdf.grid(row=0, column=2, padx=6)

text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=90, height=28)
text_box.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

root.mainloop()
