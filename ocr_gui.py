import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image
import pytesseract
import cv2
import os
from fpdf import FPDF  # For PDF export

# Path to Tesseract OCR
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# Main window
root = tk.Tk()
root.title("SnapText – Dark Mode OCR Tool")
root.geometry("720x560")
root.state('zoomed')
root.resizable(True, True)
root.configure(bg="#121212")  # Dark background

# Text box
text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12),
                                     bg="#1e1e1e", fg="#ffffff", bd=2, relief="sunken",
                                     insertbackground="white")
text_box.pack(expand=True, fill="both", padx=15, pady=15)

# Available languages
LANGUAGES = {
    "English": "eng",
    "Hindi": "hin",
    "Spanish": "spa",
    "French": "fra",
    "German": "deu"
}
selected_lang = tk.StringVar(root)
selected_lang.set("English")

# Dropdown menu
lang_menu = tk.OptionMenu(root, selected_lang, *LANGUAGES.keys())
lang_menu.config(bg="#1e1e1e", fg="#ffffff", width=15, highlightthickness=0)
lang_menu["menu"].config(bg="#1e1e1e", fg="#ffffff")
lang_menu.pack(pady=5)

# Step 4: Improved OCR function with preprocessing
def run_ocr(image_path):
    if not os.path.exists(image_path):
        return "❌ File not found!"
    img = cv2.imread(image_path)
    if img is None:
        return "❌ Unable to read image!"
    
    # Grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Resize small images
    height, width = gray.shape
    if width < 800:
        scale = 800 / width
        gray = cv2.resize(gray, (int(width*scale), int(height*scale)), interpolation=cv2.INTER_LINEAR)
    
    # Remove noise
    gray = cv2.medianBlur(gray, 3)
    
    # Adaptive thresholding
    thresh = cv2.adaptiveThreshold(gray, 255,
                                   cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                   cv2.THRESH_BINARY, 11, 2)
    
    temp_file = "temp_snaptext_ocr.png"
    cv2.imwrite(temp_file, thresh)
    
    try:
        text = pytesseract.image_to_string(Image.open(temp_file), lang=LANGUAGES[selected_lang.get()])
    except Exception as e:
        text = f"❌ OCR error: {e}"
    finally:
        try:
            os.remove(temp_file)
        except Exception:
            pass
    return text.strip()

# Upload multiple images
def upload_images():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.tiff *.tif")])
    if file_paths:
        full_text = ""
        for file_path in file_paths:
            full_text += run_ocr(file_path) + "\n\n"
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, full_text.strip())

# Save as .txt
def save_text():
    text = text_box.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("Saved", f"Text saved to {save_path}")

# Save as PDF
def save_pdf():
    text = text_box.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
    if not save_path:
        return
    try:
        pdf = FPDF()
        pdf.add_page()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.set_font("Arial", size=12)
        safe_text = text.encode("latin-1", "replace").decode("latin-1")
        for para in safe_text.splitlines():
            if para.strip() == "":
                pdf.ln(5)
            else:
                pdf.multi_cell(0, 8, para)
        pdf.output(save_path)
        messagebox.showinfo("Saved", f"PDF saved to {save_path}")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create PDF:\n{e}")

# Buttons frame
top_bar = tk.Frame(root, bg="#1e1e1e", pady=5)
top_bar.pack(pady=5)

btn_font = ("Helvetica", 11, "bold")  # Bold font

btn_upload = tk.Button(top_bar, text="Select Images", command=upload_images,
                       width=18, bg="white", fg="black", font=btn_font,
                       activebackground="#e0e0e0", relief="raised", bd=2)
btn_upload.grid(row=0, column=0, padx=6)

btn_save_txt = tk.Button(top_bar, text="Save as .txt", command=save_text,
                         width=18, bg="white", fg="black", font=btn_font,
                         activebackground="#e0e0e0", relief="raised", bd=2)
btn_save_txt.grid(row=0, column=1, padx=6)

btn_save_pdf = tk.Button(top_bar, text="Save as .pdf", command=save_pdf,
                         width=18, bg="white", fg="black", font=btn_font,
                         activebackground="#e0e0e0", relief="raised", bd=2)
btn_save_pdf.grid(row=0, column=2, padx=6)

# Run GUI
root.mainloop()