import json
import os
import sys
import tkinter as tk
from tkinter import ttk

# =========================
# SAFE PATH (PyInstaller support)
# =========================

def resource_path(relative_path):
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

# =========================
# APPDATA SAVE LOCATION (IMPORTANT FIX)
# =========================

APP_NAME = "PaliaFurnitureTracker"
APPDATA_DIR = os.path.join(os.environ["APPDATA"], APP_NAME)
os.makedirs(APPDATA_DIR, exist_ok=True)

USER_FILE = os.path.join(APPDATA_DIR, "user_data.json")

# bundled read-only files
FURNITURE_FILE = "furniture_data.json"
LAYOUT_FILE = "layout_data.json"

# =========================
# LOAD DATA
# =========================

with open(resource_path(FURNITURE_FILE), "r", encoding="utf-8") as f:
    furniture_data = json.load(f)

layout_data = {}
if os.path.exists(resource_path(LAYOUT_FILE)):
    with open(resource_path(LAYOUT_FILE), "r", encoding="utf-8") as f:
        layout_data = json.load(f)

if os.path.exists(USER_FILE):
    with open(USER_FILE, "r", encoding="utf-8") as f:
        user_data = json.load(f)
else:
    user_data = {}

# ensure structure exists
for set_name, items in furniture_data.items():
    user_data.setdefault(set_name, {})
    for item in items:
        user_data[set_name].setdefault(item, False)

def save_data():
    with open(USER_FILE, "w", encoding="utf-8") as f:
        json.dump(user_data, f, indent=2)

# =========================
# UI COLORS
# =========================

BG = "#17141d"
PANEL = "#221c2a"
ACCENT = "#a58bb7"
TEXT = "#f4ead7"
TEXT_DIM = "#b9a9c8"
CHECK = "#7ea07e"
RED = "#7a4a4a"

FONT_TITLE = ("Georgia", 18, "bold")
FONT_NORMAL = ("Georgia", 11)

# =========================
# WINDOW
# =========================

root = tk.Tk()
root.title("🌙 Cozy Furniture Tracker")
root.geometry("1250x850")
root.configure(bg=BG)

style = ttk.Style()
style.theme_use("clam")
style.configure("TProgressbar", background=ACCENT, troughcolor=PANEL)

# =========================
# STATE
# =========================

current_set = None
item_rows = []

# =========================
# LEFT PANEL
# =========================

left = tk.Frame(root, bg=PANEL, width=280)
left.pack(side="left", fill="y")

tk.Label(
    left,
    text="🌙 Furniture Sets",
    bg=PANEL,
    fg=TEXT,
    font=FONT_TITLE
).pack(pady=15)

search_var = tk.StringVar()

tk.Entry(
    left,
    textvariable=search_var,
    bg="#2a2232",
    fg=TEXT,
    insertbackground=TEXT,
    relief="flat",
    font=FONT_NORMAL
).pack(fill="x", padx=10, pady=(0, 10))

set_listbox = tk.Listbox(
    left,
    bg="#2a2232",
    fg=TEXT,
    selectbackground=ACCENT,
    relief="flat",
    font=FONT_NORMAL
)
set_listbox.pack(fill="both", expand=True, padx=10, pady=10)

# =========================
# LEFT PANEL TEXT (WITH PROGRESS %)
# =========================

def get_completion_text(set_name):
    owned = sum(user_data.get(set_name, {}).values())
    total = len(furniture_data.get(set_name, {}))
    percent = (owned / total * 100) if total else 0

    return f"{set_name} ({owned}/{total}) {percent:.0f}%"

def refresh_sets(*args):
    set_listbox.delete(0, tk.END)
    q = search_var.get().lower().strip()

    for set_name, items in furniture_data.items():
        set_match = q in set_name.lower()
        item_match = any(q in item.lower() for item in items)

        if q == "" or set_match or item_match:
            set_listbox.insert(tk.END, get_completion_text(set_name))

search_var.trace_add("write", refresh_sets)
refresh_sets()

# =========================
# RIGHT PANEL
# =========================

right = tk.Frame(root, bg=BG)
right.pack(side="right", fill="both", expand=True)

set_title = tk.Label(
    right,
    text="Select a Set",
    bg=BG,
    fg=TEXT,
    font=("Georgia", 22, "bold")
)
set_title.pack(pady=(20, 10))

progress_label = tk.Label(right, text="", bg=BG, fg=TEXT_DIM, font=FONT_NORMAL)
progress_label.pack()

progress_bar = ttk.Progressbar(right, length=500)
progress_bar.pack(pady=10)

button_frame = tk.Frame(right, bg=BG)
button_frame.pack(pady=5)

# =========================
# PROGRESS UPDATE
# =========================

def update_progress(set_name):
    owned = sum(user_data[set_name].values())
    total = len(furniture_data[set_name])
    percent = (owned / total * 100) if total else 0

    progress_label.config(text=f"{owned}/{total} collected ({percent:.1f}%)")
    progress_bar["value"] = percent

# =========================
# ACTION BUTTONS
# =========================

def complete_all():
    if not current_set:
        return
    for i in furniture_data[current_set]:
        user_data[current_set][i] = True
    save_data()
    load_set(current_set)
    refresh_sets()

def clear_all():
    if not current_set:
        return
    for i in furniture_data[current_set]:
        user_data[current_set][i] = False
    save_data()
    load_set(current_set)
    refresh_sets()

tk.Button(button_frame, text="✨ Complete All", bg=ACCENT, fg=TEXT, command=complete_all).pack(side="left", padx=5)
tk.Button(button_frame, text="🧹 Clear All", bg=RED, fg=TEXT, command=clear_all).pack(side="left", padx=5)

# =========================
# SCROLL AREA
# =========================

container = tk.Frame(right, bg=BG)
container.pack(fill="both", expand=True)

canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
scrollbar = ttk.Scrollbar(container, command=canvas.yview)
canvas.configure(yscrollcommand=scrollbar.set)

scrollbar.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)

grid_frame = tk.Frame(canvas, bg=BG)
window = canvas.create_window((0, 0), window=grid_frame, anchor="nw")

def update_scroll():
    grid_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))

grid_frame.bind("<Configure>", lambda e: update_scroll())

def fit_width(event):
    canvas.itemconfig(window, width=event.width)

canvas.bind("<Configure>", fit_width)

# =========================
# ITEM GRID
# =========================

def create_pool(size):
    global item_rows

    for w in grid_frame.winfo_children():
        w.destroy()

    item_rows = []

    for i in range(size):
        var = tk.BooleanVar()

        frame = tk.Frame(grid_frame, bg=PANEL, padx=8, pady=6)
        cb = tk.Checkbutton(
            frame,
            text="",
            variable=var,
            bg=PANEL,
            fg=TEXT,
            selectcolor=CHECK,
            activebackground=PANEL,
            activeforeground=TEXT,
            anchor="w",
            font=FONT_NORMAL,
            width=40
        )
        cb.pack(fill="both", expand=True)

        item_rows.append((frame, cb, var))

def load_set(set_name):
    global current_set

    current_set = set_name
    set_title.config(text=f"🕯️ {set_name}")

    items = list(furniture_data[set_name].keys())

    update_progress(set_name)

    if len(item_rows) != len(items):
        create_pool(len(items))

    cols = max(1, canvas.winfo_width() // 280)

    for i, item in enumerate(items):
        frame, cb, var = item_rows[i]

        var.set(user_data[set_name][item])
        cb.config(text=item)

        def toggle(i=item, v=var):
            user_data[set_name][i] = v.get()
            save_data()
            update_progress(set_name)
            refresh_sets()   # updates left panel instantly

        var.trace_add("write", lambda *_, t=toggle: t())

        row = i // cols
        col = i % cols

        frame.grid(row=row, column=col, padx=10, pady=8, sticky="nsew")

    update_scroll()

# =========================
# SET SELECTION
# =========================

def on_select(event):
    if not set_listbox.curselection():
        return

    name = set_listbox.get(set_listbox.curselection()[0]).split(" (")[0]
    load_set(name)

set_listbox.bind("<<ListboxSelect>>", on_select)

# =========================
# START
# =========================

root.mainloop()