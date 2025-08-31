import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import pytesseract
import cv2
import os

# Windows users: set path to Tesseract executable
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def run_ocr(image_path):
    """Extract text from image"""
    if not os.path.exists(image_path):
        return "❌ File not found!"

    img = cv2.imread(image_path)
    if img is None:
        return "❌ Unable to read image!"

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    temp_file = "temp.png"
    cv2.imwrite(temp_file, thresh)
    text = pytesseract.image_to_string(Image.open(temp_file))
    os.remove(temp_file)
    return text.strip()

def open_file():
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.png *.jpg *.jpeg *.bmp")]
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
        defaultextension=".txt",
        filetypes=[("Text files", "*.txt")]
    )
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            f.write(text)
        messagebox.showinfo("Saved", f"Text saved to {save_path}")

# Tkinter GUI
root = tk.Tk()
root.title("Screenshot OCR Tool")
root.geometry("600x500")

btn_open = tk.Button(root, text="Select Image", command=open_file, width=20)
btn_open.pack(pady=10)

btn_save = tk.Button(root, text="Save Text as .txt", command=save_text, width=20)
btn_save.pack(pady=5)

text_box = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=25)
text_box.pack(padx=10, pady=10)

root.mainloop()
