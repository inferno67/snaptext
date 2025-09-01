import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageGrab
import pytesseract
import cv2
import numpy as np
import os
from fpdf import FPDF
import threading
import json

# Optional libraries
try:
    import pyperclip
    clipboard_available = True
except ImportError:
    clipboard_available = False

try:
    import mss
except ImportError:
    mss = None

try:
    import keyboard
except ImportError:
    keyboard = None

# ---------- Tesseract Path ----------
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# ---------- Main Window ----------
root = tk.Tk()
root.title("SnapText Ultimate OCR")
root.geometry("1000x650")
root.state('zoomed')
root.configure(bg="#121212")

# ---------- Text Box ----------
text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Arial", 12),
                                     bg="#1e1e1e", fg="#ffffff", bd=2, relief="sunken",
                                     insertbackground="white")
text_box.pack(expand=True, fill="both", padx=15, pady=(15,5))

# ---------- OCR History ----------
ocr_history = []

history_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, height=8,
                                        bg="#1e1e1e", fg="#ffffff", font=("Arial",10))
history_box.pack(fill="x", padx=15, pady=(0,10))

def add_to_history(text):
    global ocr_history
    ocr_history.append(text)
    history_box.insert(tk.END, f"{len(ocr_history)}. {text[:100]}...\n")
    history_box.yview(tk.END)

# ---------- Status & Progress ----------
status_var = tk.StringVar()
status_var.set("Ready")
status_bar = tk.Label(root, textvariable=status_var, bg="#1e1e1e", fg="#ffffff", anchor="w", font=("Helvetica",10))
status_bar.pack(fill="x", padx=15, pady=(0,5))

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
selected_langs = []

def toggle_lang(lang, var):
    if var.get():
        if lang not in selected_langs:
            selected_langs.append(lang)
    else:
        if lang in selected_langs:
            selected_langs.remove(lang)

lang_frame = tk.Frame(root, bg="#1e1e1e")
lang_frame.pack(pady=5)
lang_vars = {}
for i, lang in enumerate(LANGUAGES.keys()):
    var = tk.BooleanVar()
    chk = tk.Checkbutton(lang_frame, text=lang, variable=var, bg="#1e1e1e", fg="#ffffff",
                         selectcolor="#444444", activebackground="#1e1e1e",
                         command=lambda l=lang, v=var: toggle_lang(l,v))
    chk.grid(row=0, column=i, padx=5)
    lang_vars[lang] = var
    if lang == "English":
        var.set(True)
        selected_langs.append(lang)

# ---------- Preprocessing Options ----------
pre_frame = tk.Frame(root, bg="#1e1e1e")
pre_frame.pack(pady=5)
pre_vars = {}
pre_options = ["Grayscale", "CLAHE", "Noise Removal", "Sharpening", "Adaptive Thresholding"]
for i, opt in enumerate(pre_options):
    var = tk.BooleanVar(value=True)
    chk = tk.Checkbutton(pre_frame, text=opt, variable=var, bg="#1e1e1e", fg="#ffffff",
                         selectcolor="#444444", activebackground="#1e1e1e")
    chk.grid(row=0, column=i, padx=5)
    pre_vars[opt] = var

# ---------- Load/Save Preprocessing Presets ----------
PRESET_FILE = "preprocessing_presets.json"

def save_presets():
    data = {k: v.get() for k,v in pre_vars.items()}
    with open(PRESET_FILE, "w") as f:
        json.dump(data, f)
    messagebox.showinfo("Saved", "Preprocessing preset saved!")

def load_presets():
    if os.path.exists(PRESET_FILE):
        with open(PRESET_FILE, "r") as f:
            data = json.load(f)
        for k,v in pre_vars.items():
            if k in data:
                v.set(data[k])
        messagebox.showinfo("Loaded", "Preprocessing preset loaded!")

# ---------- OCR Function ----------
def run_ocr(image_path):
    if not os.path.exists(image_path):
        return "❌ File not found!"
    img = cv2.imread(image_path)
    if img is None:
        return "❌ Unable to read image!"

    h, w = img.shape[:2]
    if w < 1200:
        scale = 1200 / w
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_LINEAR)

    gray = img.copy()
    if pre_vars["Grayscale"].get():
        gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
    if pre_vars["CLAHE"].get():
        clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
        gray = clahe.apply(gray)
    if pre_vars["Noise Removal"].get():
        gray = cv2.medianBlur(gray, 3)
    if pre_vars["Sharpening"].get():
        kernel = np.array([[0,-1,0],[-1,5,-1],[0,-1,0]])
        gray = cv2.filter2D(gray, -1, kernel)
    if pre_vars["Adaptive Thresholding"].get():
        gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                     cv2.THRESH_BINARY, 11, 2)

    temp_file = "temp_snaptext_ocr.png"
    cv2.imwrite(temp_file, gray)

    try:
        lang_codes = '+'.join([LANGUAGES[l] for l in selected_langs]) if selected_langs else 'eng'
        custom_config = f'-l {lang_codes} --psm 6'
        text = pytesseract.image_to_string(Image.open(temp_file), config=custom_config)
    except Exception as e:
        text = f"❌ OCR error: {e}"
    finally:
        try:
            os.remove(temp_file)
        except:
            pass
    return text.strip()

# ---------- Multi-Image OCR ----------
def process_files(file_paths):
    full_text = ""
    total = len(file_paths)
    progress["maximum"] = total
    for i, file_path in enumerate(file_paths, start=1):
        status_var.set(f"Processing {i}/{total}: {os.path.basename(file_path)}")
        root.update_idletasks()
        full_text += run_ocr(file_path) + "\n\n"

    text_box.delete(1.0, tk.END)
    text_box.insert(tk.END, full_text.strip())

    add_to_history(full_text.strip())

    if clipboard_available:
        try:
            pyperclip.copy(full_text.strip()) # type: ignore
        except:
            pass

    status_var.set("OCR completed!")
    progress["value"] = 0

def upload_images():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files","*.png *.jpg *.jpeg *.bmp *.tiff *.tif")])
    if file_paths:
        threading.Thread(target=process_files, args=(file_paths,)).start()

# ---------- Screenshot OCR ----------
def capture_screenshot():
    status_var.set("Capturing screenshot...")
    root.update_idletasks()
    screenshot = ImageGrab.grab()
    temp_file = "temp_screenshot.png"
    screenshot.save(temp_file)
    process_files([temp_file])
    try:
        os.remove(temp_file)
    except:
        pass
    status_var.set("Screenshot OCR completed!")

# ---------- Partial Screen OCR ----------
def partial_ocr():
    if mss is None:
        messagebox.showwarning("Warning", "mss library not installed!")
        return
    with mss.mss() as sct:
        bbox = sct.monitors[1]  # full screen; user can adjust
        img = np.array(sct.grab(bbox))
        temp_file = "temp_partial.png"
        cv2.imwrite(temp_file, cv2.cvtColor(img, cv2.COLOR_RGBA2BGR))
    process_files([temp_file])
    try:
        os.remove(temp_file)
    except:
        pass

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
btn_bg, btn_fg = "white", "black"

buttons = [
    ("Select Images", upload_images),
    ("Save as .txt", save_text),
    ("Save as .pdf", save_pdf),
    ("Screenshot OCR", capture_screenshot),
    ("Partial OCR", partial_ocr),
    ("Save Preset", save_presets),
    ("Load Preset", load_presets)
]

for i, (text, func) in enumerate(buttons):
    b = tk.Button(top_bar, text=text, command=func, width=18, bg=btn_bg, fg=btn_fg,
                  font=btn_font, activebackground="#e0e0e0", relief="raised", bd=2)
    b.grid(row=0, column=i, padx=4)

# ---------- Global Hotkey for Screenshot OCR ----------
if keyboard:
    def hotkey_screenshot():
        capture_screenshot()
    threading.Thread(target=lambda: keyboard.add_hotkey("ctrl+shift+s", hotkey_screenshot)).start() # type: ignore

# ---------- Run GUI ----------
root.mainloop()