import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image
import pytesseract
import cv2
import numpy as np
import os
from fpdf import FPDF
import threading

# ---------- Tesseract Path ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- Main Window ----------
root = tk.Tk()
root.title("SnapText – OCR Enhanced Accuracy")
root.geometry("800x600")
root.state('zoomed')
root.resizable(True, True)
root.configure(bg="#121212")

# ---------- Text Box ----------
text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12),
                                     bg="#1e1e1e", fg="#ffffff", bd=2, relief="sunken",
                                     insertbackground="white")
text_box.pack(expand=True, fill="both", padx=15, pady=(15,5))

# ---------- Status Bar ----------
status_var = tk.StringVar()
status_var.set("Ready")
status_bar = tk.Label(root, textvariable=status_var, bg="#1e1e1e", fg="#ffffff", anchor="w", font=("Helvetica",10))
status_bar.pack(fill="x", padx=15, pady=(0,5))

# ---------- Progress Bar ----------
progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
progress.pack(pady=(0,10))

# ---------- Languages ----------
LANGUAGES = {
    "English": "eng",
    "Hindi": "hin",
    "Spanish": "spa",
    "French": "fra",
    "German": "deu"
}
selected_lang = tk.StringVar(root)
selected_lang.set("English")

lang_menu = tk.OptionMenu(root, selected_lang, *LANGUAGES.keys())
lang_menu.config(bg="#1e1e1e", fg="#ffffff", width=15, highlightthickness=0)
lang_menu["menu"].config(bg="#1e1e1e", fg="#ffffff")
lang_menu.pack(pady=5)

# ---------- OCR Function with maximum preprocessing ----------
def run_ocr(image_path):
    if not os.path.exists(image_path):
        return "❌ File not found!"
    img = cv2.imread(image_path)
    if img is None:
        return "❌ Unable to read image!"

    # Resize small images
    h, w = img.shape[:2]
    if w < 1200:
        scale = 1200 / w
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_LINEAR)

    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # CLAHE contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    gray = clahe.apply(gray)

    # Noise removal
    gray = cv2.medianBlur(gray, 3)

    # Sharpening
    kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
    gray = cv2.filter2D(gray, -1, kernel)

    # Adaptive thresholding
    gray = cv2.adaptiveThreshold(gray, 255,
                                 cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                 cv2.THRESH_BINARY, 11, 2)

    # Dilation to strengthen faint text
    kernel_d = np.ones((2,2), np.uint8)
    gray = cv2.dilate(gray, kernel_d, iterations=1)

    temp_file = "temp_snaptext_ocr.png"
    cv2.imwrite(temp_file, gray)

    try:
        custom_config = f'-l {LANGUAGES[selected_lang.get()]} --psm 6'
        text = pytesseract.image_to_string(Image.open(temp_file), config=custom_config)
    except Exception as e:
        text = f"❌ OCR error: {e}"
    finally:
        try:
            os.remove(temp_file)
        except Exception:
            pass
    return text.strip()

# ---------- Multi-Image Processing ----------
def process_files(file_paths):
    full_text = ""
    total = len(file_paths)
    progress["maximum"] = total
    for i, file_path in enumerate(file_paths, start=1):
        status_var.set(f"Processing {i}/{total}: {os.path.basename(file_path)}")
        root.update_idletasks()
        full_text += run_ocr(file_path) + "\n\n"
        progress["value"] = i
    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, full_text.strip())
    status_var.set("OCR completed!")
    progress["value"] = 0

def upload_images():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files","*.png *.jpg *.jpeg *.bmp *.tiff *.tif")])
    if file_paths:
        threading.Thread(target=process_files, args=(file_paths,)).start()

# ---------- Drag & Drop ----------
def drop(event):
    files = root.tk.splitlist(event.data)
    threading.Thread(target=process_files, args=(files,)).start()

try:
    import tkinterdnd2 as tkdnd
    text_box.drop_target_register(tkdnd.DND_FILES) # type: ignore
    text_box.dnd_bind('<<Drop>>', drop) # type: ignore
except:
    pass

# ---------- Save Functions ----------
def save_text():
    text = text_box.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")])
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("Saved", f"Text saved to {save_path}")

def save_pdf():
    text = text_box.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files","*.pdf")])
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

# ---------- Buttons ----------
top_bar = tk.Frame(root, bg="#1e1e1e", pady=5)
top_bar.pack(pady=5)

btn_font = ("Helvetica", 11, "bold")

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

# ---------- Run GUI ----------
root.mainloop()
