# app.py
import tkinter as tk
from tkinter import filedialog, scrolledtext, messagebox
from tkinter import ttk
from summarizer import generate_summary_and_title
from docx import Document
import PyPDF2
import os

# ---------- File reading helpers ----------
def read_text_file(path):
    with open(path, 'r', encoding='utf8', errors='ignore') as f:
        return f.read()

def read_pdf_file(path):
    text = ""
    with open(path, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            try:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + " "
            except Exception:
                continue
    return text

def read_docx_file(path):
    doc = Document(path)
    text = " ".join([p.text for p in doc.paragraphs])
    return text

def read_file(filepath):
    ext = os.path.splitext(filepath)[1].lower()
    try:
        if ext == '.txt':
            return read_text_file(filepath)
        elif ext == '.pdf':
            return read_pdf_file(filepath)
        elif ext == '.docx':
            return read_docx_file(filepath)
    except Exception as e:
        messagebox.showerror("File Read Error", str(e))
    messagebox.showerror("Unsupported", "Please upload a .txt, .pdf or .docx file.")
    return ""

# ---------- GUI ----------
root = tk.Tk()
root.title("Dudu's Smart Summarizer 💖")
root.geometry("1000x740")
root.config(bg="#fff0fb")

# Top label
tk.Label(root, text="Paste text or upload a document:", bg="#fff0fb", font=("Helvetica", 14, "bold")).pack(pady=8)

# Buttons frame
btn_frame = tk.Frame(root, bg="#fff0fb")
btn_frame.pack(pady=6)

def upload_action():
    file_path = filedialog.askopenfilename(
        filetypes=[("Text files", "*.txt"), ("PDF files", "*.pdf"), ("Word files", "*.docx")]
    )
    if file_path:
        content = read_file(file_path)
        input_text.delete("1.0", tk.END)
        input_text.insert(tk.END, content)

upload_btn = tk.Button(btn_frame, text="Upload File 📄", command=upload_action, bg="#f7c7ff", font=("Helvetica", 11))
upload_btn.pack(side=tk.LEFT, padx=8)

# Algorithm choice
algo_var = tk.StringVar(value='textrank')
tk.Label(btn_frame, text="Algorithm:", bg="#fff0fb", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=(16,4))
ttk.Radiobutton(btn_frame, text="TextRank", variable=algo_var, value='textrank').pack(side=tk.LEFT)
ttk.Radiobutton(btn_frame, text="TF-IDF", variable=algo_var, value='tfidf').pack(side=tk.LEFT)
ttk.Radiobutton(btn_frame, text="Frequency", variable=algo_var, value='frequency').pack(side=tk.LEFT)

# Slider for number of sentences
slider_frame = tk.Frame(root, bg="#fff0fb")
slider_frame.pack(pady=6)
tk.Label(slider_frame, text="Number of sentences:", bg="#fff0fb", font=("Helvetica", 11)).pack(side=tk.LEFT, padx=6)
num_sent_var = tk.IntVar(value=3)
num_slider = tk.Scale(slider_frame, from_=1, to=8, orient=tk.HORIZONTAL, variable=num_sent_var)
num_slider.pack(side=tk.LEFT)

# Input text area
input_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=110, height=14, font=("Arial", 10))
input_text.pack(padx=12, pady=10)

# Summarize button
def summarize_action():
    text = input_text.get("1.0", tk.END).strip()
    if not text:
        messagebox.showwarning("Empty Input", "Please paste text or upload a file, dudu 💕")
        return
    try:
        method = algo_var.get()
        n = num_sent_var.get()
        summary, title = generate_summary_and_title(text, num_sentences=n, method=method)
        output_text.delete("1.0", tk.END)
        output_text.insert(tk.END, summary)
        title_var.set(title)
    except Exception as e:
        messagebox.showerror("Error", str(e))

summarize_btn = tk.Button(root, text="Summarize ✨", command=summarize_action, bg="#d8a6ff", font=("Helvetica", 12, "bold"))
summarize_btn.pack(pady=8)

# Title display
title_var = tk.StringVar(value="")
title_label = tk.Label(root, textvariable=title_var, bg="#fff0fb", fg="#7a007a", font=("Helvetica", 13, "italic"))
title_label.pack(pady=6)

# Output (summary)
tk.Label(root, text="Summary:", bg="#fff0fb", font=("Helvetica", 14, "bold")).pack(pady=4)
output_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=110, height=12, font=("Arial", 10))
output_text.pack(padx=12, pady=6)

# Bottom buttons (Save / Clear)
def save_summary():
    summary = output_text.get("1.0", tk.END).strip()
    if not summary:
        messagebox.showwarning("Empty", "No summary to save, dudu 💕")
        return
    default_name = (title_var.get() or "summary").replace(" ", "_") + ".txt"
    path = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=default_name,
                                        filetypes=[("Text files", "*.txt")])
    if path:
        with open(path, 'w', encoding='utf8') as f:
            f.write("Title: " + (title_var.get() or "") + "\n\n")
            f.write(summary)
        messagebox.showinfo("Saved", f"Summary saved to {path}")

def clear_all():
    input_text.delete("1.0", tk.END)
    output_text.delete("1.0", tk.END)
    title_var.set("")

bottom_frame = tk.Frame(root, bg="#fff0fb")
bottom_frame.pack(pady=8)
save_btn = tk.Button(bottom_frame, text="Save Summary 💾", command=save_summary, bg="#ffd7f7")
save_btn.pack(side=tk.LEFT, padx=8)
clear_btn = tk.Button(bottom_frame, text="Clear ✖️", command=clear_all, bg="#ffeef9")
clear_btn.pack(side=tk.LEFT, padx=8)

root.mainloop()
