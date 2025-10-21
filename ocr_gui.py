#!/usr/bin/env python3
import os
import sys
import threading
import json
import tempfile
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
from PIL import Image, ImageGrab, UnidentifiedImageError
import pytesseract
import cv2
import numpy as np
from fpdf import FPDF

# Optional libraries
try:
    import pyperclip
    clipboard_available = True
except Exception:
    pyperclip = None
    clipboard_available = False

try:
    import mss
    import mss.tools
except Exception:
    mss = None

try:
    import keyboard
except Exception:
    keyboard = None

# ---------- Tesseract Path ----------
# If user is on Windows and has tesseract in the default install location, keep it.
# If TESSERACT_CMD env var exists, use it. Otherwise assume tesseract is in PATH.
if "TESSERACT_CMD" in os.environ:
    pytesseract.pytesseract.tesseract_cmd = os.environ["TESSERACT_CMD"]
else:
    if sys.platform.startswith("win"):
        default_win_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        if os.path.exists(default_win_path):
            pytesseract.pytesseract.tesseract_cmd = default_win_path
        # else rely on PATH (user must have tesseract on PATH)
    # On Linux/Mac we typically rely on system tesseract in PATH

# ---------- Main Window ----------
root = tk.Tk()
root.title("SnapText Ultimate OCR")
root.geometry("1000x650")
root.configure(bg="#121212")

# Cross-platform "maximized" / fullscreen fallback
def maximize_window(win):
    try:
        win.state('zoomed')  # windows
    except tk.TclError:
        try:
            win.attributes('-zoomed', True)  # some linux
        except tk.TclError:
            try:
                win.attributes('-fullscreen', True)  # fallback
            except tk.TclError:
                pass

maximize_window(root)

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
    display = (text[:120] + "...") if len(text) > 120 else text
    history_box.insert(tk.END, f"{len(ocr_history)}. {display}\n")
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
PRESET_FILE = os.path.join(os.path.expanduser("~"), ".snaptext_presets.json")

def save_presets():
    data = {k: bool(v.get()) for k,v in pre_vars.items()}
    try:
        with open(PRESET_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
        messagebox.showinfo("Saved", "Preprocessing preset saved!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save preset:\n{e}")

def load_presets():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            for k,v in pre_vars.items():
                if k in data:
                    v.set(bool(data[k]))
            messagebox.showinfo("Loaded", "Preprocessing preset loaded!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load preset:\n{e}")
    else:
        messagebox.showinfo("No Preset", "No preset file found.")

# ---------- Helpers ----------
_temp_dir = tempfile.mkdtemp(prefix="snaptext_")
def _get_temp_file(suffix=".png"):
    return os.path.join(_temp_dir, f"temp_{threading.get_ident()}{suffix}")

def _cleanup_temp_dir():
    try:
        shutil.rmtree(_temp_dir)
    except Exception:
        pass

# ---------- OCR Function ----------
def run_ocr(image_path):
    if not os.path.exists(image_path):
        return "❌ File not found!"
    # read with OpenCV
    img = cv2.imread(image_path)
    if img is None:
        # try pillow fallback
        try:
            pil = Image.open(image_path).convert("RGB")
            img = cv2.cvtColor(np.array(pil), cv2.COLOR_RGB2BGR)
        except Exception:
            return "❌ Unable to read image!"

    h, w = img.shape[:2]
    if w < 1200:
        scale = 1200 / w
        img = cv2.resize(img, (int(w*scale), int(h*scale)), interpolation=cv2.INTER_LINEAR)

    gray = img.copy()
    try:
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
            if len(gray.shape) == 3:
                gray = cv2.cvtColor(gray, cv2.COLOR_BGR2GRAY)
            gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                         cv2.THRESH_BINARY, 11, 2)
    except Exception as e:
        # If preprocessing fails, continue with original image
        print("Preprocessing error:", e)

    temp_file = _get_temp_file(".png")
    try:
        cv2.imwrite(temp_file, gray)
    except Exception as e:
        return f"❌ Failed to write temp file: {e}"

    try:
        lang_codes = '+'.join([LANGUAGES[l] for l in selected_langs]) if selected_langs else 'eng'
        custom_config = f'-l {lang_codes} --psm 6'
        text = pytesseract.image_to_string(Image.open(temp_file), config=custom_config)
    except Exception as e:
        text = f"❌ OCR error: {e}"
    finally:
        try:
            os.remove(temp_file)
        except Exception:
            pass
    return text.strip()

# ---------- Multi-File OCR Pipeline ----------
def _process_files_thread(file_paths):
    try:
        full_text = ""
        total = len(file_paths)
        progress["maximum"] = total
        for i, file_path in enumerate(file_paths, start=1):
            status_var.set(f"Processing {i}/{total}: {os.path.basename(file_path)}")
            root.update_idletasks()
            txt = run_ocr(file_path)
            full_text += txt + "\n\n"
            progress["value"] = i
        text_box.delete(1.0, tk.END)
        text_box.insert(tk.END, full_text.strip())
        add_to_history(full_text.strip())
        if clipboard_available and full_text.strip():
            try:
                pyperclip.copy(full_text.strip())  # type: ignore
                status_var.set("OCR completed! (copied to clipboard)")
            except Exception:
                status_var.set("OCR completed!")
        else:
            status_var.set("OCR completed!")
    except Exception as e:
        messagebox.showerror("Error", f"Processing failed:\n{e}")
        status_var.set("Ready")
    finally:
        progress["value"] = 0
        # re-enable buttons if you choose to disable them in upload_images

def process_files_async(file_paths):
    threading.Thread(target=_process_files_thread, args=(file_paths,), daemon=True).start()

def upload_images():
    file_paths = filedialog.askopenfilenames(filetypes=[("Image Files","*.png *.jpg *.jpeg *.bmp *.tiff *.tif"), ("PDF","*.pdf")])
    if file_paths:
        # If any PDF selected, convert pages to images
        expanded_paths = []
        for p in file_paths:
            if p.lower().endswith(".pdf"):
                try:
                    from pdf2image import convert_from_path
                    pages = convert_from_path(p)
                    for idx, pg in enumerate(pages):
                        tmp = _get_temp_file(f"_pdfpage_{idx}.png")
                        pg.save(tmp, "PNG")
                        expanded_paths.append(tmp)
                except Exception as e:
                    messagebox.showerror("PDF Error", f"Failed to convert PDF {os.path.basename(p)}:\n{e}")
            else:
                expanded_paths.append(p)
        if expanded_paths:
            process_files_async(expanded_paths)

# ---------- Screenshot OCR ----------
def capture_screenshot():
    status_var.set("Capturing screenshot...")
    root.update_idletasks()
    temp_file = _get_temp_file(".png")
    try:
        # Try PIL ImageGrab (works on Windows and macOS)
        try:
            img = ImageGrab.grab()
            img.save(temp_file)
        except (OSError, ValueError, UnidentifiedImageError):
            # Fallback to mss on linux or as a more robust method
            if mss is None:
                messagebox.showerror("Screenshot Error", "Automatic screenshot not available (mss not installed).")
                status_var.set("Ready")
                return
            with mss.mss() as sct:
                monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
                sct_img = sct.grab(monitor)
                mss.tools.to_png(sct_img.rgb, sct_img.size, output=temp_file)
        process_files_async([temp_file])
    except Exception as e:
        messagebox.showerror("Screenshot Error", f"Failed to capture screenshot:\n{e}")
        status_var.set("Ready")

# ---------- Partial Screen OCR ----------
def partial_ocr():
    if mss is None:
        messagebox.showwarning("Warning", "Partial OCR requires 'mss' library. Install it or use full-screen screenshot.")
        return
    status_var.set("Capturing partial screen (full monitor used by default)...")
    root.update_idletasks()
    try:
        with mss.mss() as sct:
            monitor = sct.monitors[1] if len(sct.monitors) > 1 else sct.monitors[0]
            img = sct.grab(monitor)
            temp_file = _get_temp_file(".png")
            mss.tools.to_png(img.rgb, img.size, output=temp_file)
        process_files_async([temp_file])
    except Exception as e:
        messagebox.showerror("Partial OCR Error", f"{e}")
        status_var.set("Ready")

# ---------- Drag & Drop ----------
def drop(event):
    try:
        files = root.tk.splitlist(event.data)
        process_files_async(files)
    except Exception as e:
        print("Drop error:", e)

try:
    import tkinterdnd2 as tkdnd
    # register drop on the text box (if tkdnd is installed)
    text_box.drop_target_register(tkdnd.DND_FILES)  # type: ignore
    text_box.dnd_bind('<<Drop>>', drop)  # type: ignore
except Exception:
    pass

# ---------- Save Functions ----------
def save_text():
    text = text_box.get(1.0, tk.END).strip()
    if not text:
        messagebox.showwarning("Warning", "No text to save!")
        return
    save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files","*.txt")])
    if save_path:
        try:
            with open(save_path, "w", encoding="utf-8") as f:
                f.write(text)
            messagebox.showinfo("Saved", f"Text saved to {save_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save:\n{e}")

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
        # FPDF default fonts: "Arial" is available by default; this should work cross-platform
        pdf.set_font("Arial", size=12)
        safe_text = text.replace("\t", "    ")
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
    ("Select Images / PDFs", upload_images),
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
    try:
        def hotkey_screenshot():
            capture_screenshot()
        # run the hotkey listener in a daemon thread
        threading.Thread(target=lambda: keyboard.add_hotkey("ctrl+shift+s", hotkey_screenshot), daemon=True).start()
    except Exception as e:
        print("Hotkey setup failed:", e)

# ---------- Clean up temp dir on exit ----------
def on_exit():
    try:
        _cleanup_temp_dir()
    except:
        pass
    root.destroy()

root.protocol("WM_DELETE_WINDOW", on_exit)

# ---------- Run GUI ----------
if __name__ == "__main__":
    try:
        root.mainloop()
    finally:
        _cleanup_temp_dir()
