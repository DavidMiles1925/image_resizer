import os
import glob
import re
import sys
import tkinter as tk
from tkinter import filedialog, ttk, messagebox
from PIL import Image
from PIL import ImageEnhance


CURRENT_VERSION = "1.3"
VESRION_YEAR = "2025"

DEFAULT_IMAGE_RESIZE_WIDTH = 3072
DEFAULT_IMAGE_RESIZE_HEIGHT = 3072
DEFAULT_SUFFIX = "_resized"


try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except Exception:
    DND_AVAILABLE = False


def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def resize_image(path, output_folder, target_size, keep_aspect, crop_to_fit, brightness_percent, suffix):
    """
    brightness_percent: numeric percentage (e.g. 20 for +20%, -10 for -10%, 0 for no change)
    """
    try:
        with Image.open(path) as img:
            # Apply brightness change if requested (non-zero)
            try:
                b = float(brightness_percent)
            except Exception:
                b = 0.0
            if b != 0.0:
                factor = 1.0 + (b / 100.0)
                # Prevent negative factor; factor < 0 makes no sense (clamp to 0.0 which gives black)
                factor = max(0.0, factor)
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(factor)

            if crop_to_fit:
                img = resize_and_crop(img, target_size)
            elif keep_aspect:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(target_size, Image.Resampling.LANCZOS)

            base = os.path.basename(path)
            name, ext = os.path.splitext(base)
            output_path = os.path.join(output_folder, f"{name}{suffix}{ext}")
            img.save(output_path)
            return output_path
    except Exception as e:
        print(f"Failed to resize {path}: {e}")
        return None


def process_images(input_folder, output_folder, target_size, keep_aspect, progress_bar, filename_label):
    image_paths = glob.glob(os.path.join(input_folder, "*.*"))
    image_paths = [p for p in image_paths if p.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))]

    total = len(image_paths)
    if total == 0:
        messagebox.showinfo("No Images", "No supported images found in the selected folder.")
        return

    for i, path in enumerate(image_paths, start=1):
        filename_label.config(text=os.path.basename(path))  # Update label
        resize_image(path, output_folder, target_size, keep_aspect, crop_var.get(), brightness_var.get(), suffix_entry.get())
        progress_bar["value"] = (i / total) * 100
        root.update_idletasks()

    filename_label.config(text="All done!")  # Reset text
    messagebox.showinfo("Done", f"Resized {total} images!")


def validate_size_entries():
    """Return (width, height) as integers if valid, otherwise show an error and return None."""
    w = width_entry.get().strip()
    h = height_entry.get().strip()
    if not w or not h:
        messagebox.showerror("Invalid size", "Please enter both width and height.")
        return None
    try:
        width = int(w)
        height = int(h)
        if width <= 0 or height <= 0:
            raise ValueError("Non-positive")
    except Exception:
        messagebox.showerror("Invalid size", "Width and height must be positive integers.")
        return None
    return (width, height)


def start_resize():
    sizes = validate_size_entries()
    if sizes is None:
        return

    messagebox.showinfo("Select Image Folder", "Select a folder that contains the images you want to resize.")

    input_folder = filedialog.askdirectory(title="Select Input Folder")
    if not input_folder:
        return

    messagebox.showinfo("Select Output Folder", "Select a folder where the resized images will be saved.")

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    keep_aspect = aspect_var.get()
    size = sizes
    progress_bar["value"] = 0
    process_images(input_folder, output_folder, size, keep_aspect, progress_bar, filename_label)


def start_resize_selected():
    sizes = validate_size_entries()
    if sizes is None:
        return

    messagebox.showinfo("Step 1", "Select one or more images you want to resize.")

    file_paths = filedialog.askopenfilenames(
        title="Select Image Files",
        filetypes=[("Image files", "*.jpg *.jpeg *.png *.bmp *.gif")]
    )

    if not file_paths:
        return

    messagebox.showinfo("Step 2", "Choose a folder where the resized images will be saved.")

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    size = sizes
    keep_aspect = aspect_var.get()

    total = len(file_paths)
    for i, path in enumerate(file_paths, start=1):
        filename_label.config(text=os.path.basename(path))  # Show current file
        resize_image(path, output_folder, size, keep_aspect, crop_var.get(), brightness_var.get(), suffix_entry.get())
        progress_bar["value"] = (i / total) * 100
        root.update_idletasks()

    filename_label.config(text="All done!")

    messagebox.showinfo("Done", f"Resized {total} images!")


def resize_and_crop(img, target_size):
    target_width, target_height = target_size
    img_ratio = img.width / img.height
    target_ratio = target_width / target_height

    # Resize image to cover the target size completely
    if img_ratio > target_ratio:
        # Image is wider than target ratio
        new_height = target_height
        new_width = int(new_height * img_ratio)
    else:
        # Image is taller (or equal ratio)
        new_width = target_width
        new_height = int(new_width / img_ratio)

    img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

    # Calculate coordinates to crop the center
    left = (new_width - target_width) // 2
    top = (new_height - target_height) // 2
    right = left + target_width
    bottom = top + target_height

    img = img.crop((left, top, right, bottom))
    return img


def parse_drop_files(data):
    """
    Parse the event.data string from tkinterdnd2's drop event.
    It may contain braced paths or plain paths separated by spaces.
    Example forms:
      '{C:\\path with spaces\\file.jpg} {C:\\another.jpg}'
      '/home/user/file1.jpg /home/user/file2.jpg'
    """
    parts = re.findall(r'{([^}]*)}|([^ ]+)', data)
    files = []
    for g1, g2 in parts:
        file = g1 if g1 else g2
        files.append(file)
    return files


def handle_dropped_paths(paths):
    """
    Given a list of dropped paths (files or folders), process images found.
    Save processed images in the folder they came from (for files) or in the folder itself (for folders).
    """
    sizes = validate_size_entries()
    if sizes is None:
        return

    # Expand directories to image lists; keep files as-is if they are images
    supported_exts = (".jpg", ".jpeg", ".png", ".bmp", ".gif")
    image_paths = []

    for p in paths:
        if os.path.isdir(p):
            found = glob.glob(os.path.join(p, "*.*"))
            found = [f for f in found if f.lower().endswith(supported_exts)]
            image_paths.extend(found)
        elif os.path.isfile(p):
            if p.lower().endswith(supported_exts):
                image_paths.append(p)
            else:
                # Not a supported image; skip
                pass
        else:
            # Path doesn't exist - skip
            pass

    if not image_paths:
        messagebox.showinfo("No Images", "No supported images found in the dropped items.")
        return

    total = len(image_paths)
    progress_bar["value"] = 0
    size = sizes
    keep_aspect = aspect_var.get()
    suffix = suffix_entry.get()
    brightness = brightness_var.get()
    crop = crop_var.get()

    for i, img_path in enumerate(image_paths, start=1):
        filename_label.config(text=os.path.basename(img_path))
        output_folder = os.path.dirname(img_path)  # Save in original folder as requested
        resize_image(img_path, output_folder, size, keep_aspect, crop, brightness, suffix)
        progress_bar["value"] = (i / total) * 100
        root.update_idletasks()

    filename_label.config(text="All done!")
    messagebox.showinfo("Done", f"Resized {total} images (from dropped items).")


def on_drop(event):
    """
    Handler for <<Drop>> event from tkinterdnd2. event.data contains paths.
    """
    try:
        data = event.data
        paths = parse_drop_files(data)
        handle_dropped_paths(paths)
    except Exception as e:
        messagebox.showerror("Drop Error", f"Failed to handle dropped items: {e}")


# Create main window (use TkinterDnD.Tk() if available)
if DND_AVAILABLE:
    root = TkinterDnD.Tk()
else:
    root = tk.Tk()

root.title(f"Batch Image Resizer {CURRENT_VERSION} - © {VESRION_YEAR}")
try:
    root.iconbitmap(resource_path("resize.ico"))
except Exception as e:
    print(f"Failed to load icon: {e}")

root.geometry("520x500")
root.update_idletasks()
root.minsize(root.winfo_width(), root.winfo_height())

frame = tk.Frame(root)
frame.pack(pady=10)

# Brightness control: numeric percentage (Spinbox)
bright_label = tk.Label(frame, text="Brightness (%):", font=("Arial", 10, "bold"))
bright_label.grid(row=0, column=0, pady=5, sticky="e")

brightness_var = tk.DoubleVar(value=0.0)  # default 0% (no change)
brightness_spin = tk.Spinbox(frame, from_=-100.0, to=500.0, increment=1.0, textvariable=brightness_var, width=8)
brightness_spin.grid(row=0, column=1, pady=5, sticky="w")

bright_hint = tk.Label(frame, text="(use negative to darken, positive to brighten)", font=("Arial", 8))
bright_hint.grid(row=0, column=2, columnspan=2, pady=5, sticky="w")

# Separator after Brightness section
sep1 = ttk.Separator(frame, orient="horizontal")
sep1.grid(row=1, column=0, columnspan=4, sticky="ew", pady=6)

choice_label = tk.Label(frame, text="Select up to ONE:", font=("Arial", 10, "bold"))
choice_label.grid(row=2, column=1, columnspan=2, pady=5)

aspect_var = tk.BooleanVar()
aspect_check = tk.Checkbutton(frame, text="Keep Aspect Ratio", variable=aspect_var)
aspect_check.grid(row=3, column=0, columnspan=2, pady=5)

crop_var = tk.BooleanVar()
crop_check = tk.Checkbutton(frame, text="Crop to Fit", variable=crop_var)
crop_check.grid(row=3, column=2, columnspan=2, pady=5)

# Separator after Cropping/Aspect section
sep2 = ttk.Separator(frame, orient="horizontal")
sep2.grid(row=4, column=0, columnspan=4, sticky="ew", pady=6)

suffix_label = tk.Label(frame, text="Filename suffix:", font=("Arial", 10, "bold"))
suffix_label.grid(row=5, column=1, columnspan=2, pady=5)
suffix_entry = tk.Entry(frame)
suffix_entry.insert(0, DEFAULT_SUFFIX)  # Default value
suffix_entry.grid(row=5, column=3, columnspan=2, pady=5)

# Separator after Filename/Suffix section
sep3 = ttk.Separator(frame, orient="horizontal")
sep3.grid(row=6, column=0, columnspan=4, sticky="ew", pady=6)

width_label = tk.Label(frame, text="Width:", font=("Arial", 10))
width_label.grid(row=7, column=0, pady=8, sticky="e")
width_entry = tk.Entry(frame, width=12)
width_entry.insert(0, DEFAULT_IMAGE_RESIZE_WIDTH)
width_entry.grid(row=7, column=1, pady=8, sticky="w")

height_label = tk.Label(frame, text="Height:", font=("Arial", 10))
height_label.grid(row=7, column=2, pady=8, sticky="e")
height_entry = tk.Entry(frame, width=12)
height_entry.insert(0, DEFAULT_IMAGE_RESIZE_HEIGHT)
height_entry.grid(row=7, column=3, pady=8, sticky="w")

button_label = tk.Label(frame, text="Resize folder or file(s)?", font=("Arial", 10, "bold"))
button_label.grid(row=8, column=1, columnspan=2, pady=5)

start_button = tk.Button(frame, text="Start Batch (Folder) Resize", command=start_resize)
start_button.grid(row=9, column=0, columnspan=2, pady=5)

select_button = tk.Button(frame, text="Resize Only Selected Images", command=start_resize_selected)
select_button.grid(row=9, column=2, columnspan=2, pady=5)

filename_label = tk.Label(root, text="Ready", font=("Arial", 10))
filename_label.pack(pady=5)

# Drag & Drop area
drop_frame = tk.Frame(root, relief="groove", borderwidth=2)
drop_frame.pack(padx=10, pady=5, fill="x")

drop_instructions = "Drag and drop images or folders here to process them (saved to their original folder)."
drop_label = tk.Label(drop_frame, text=drop_instructions, wraplength=480, justify="center", height=3)
drop_label.pack(fill="both", padx=6, pady=6)

if DND_AVAILABLE:
    # Register drop target for the label/frame
    try:
        drop_label.drop_target_register(DND_FILES)
        drop_label.dnd_bind('<<Drop>>', on_drop)
    except Exception as e:
        print("Failed to register drop target:", e)
        DND_AVAILABLE = False

progress_bar = ttk.Progressbar(root, orient="horizontal", length=480, mode="determinate")
progress_bar.pack(pady=10)

created_by_label = tk.Label(root, text="Created by David Miles", font=("Arial", 9, "italic"), fg="gray")
created_by_label.pack(pady=4)

# If DnD not available, inform the user (non-blocking informational message)
if not DND_AVAILABLE:
    # Show a small info on startup once
    def show_dnd_info():
        messagebox.showinfo(
            "Drag & Drop not available",
            "Drag & drop support is not available because the 'tkinterdnd2' package is not installed.\n\n"
            "To enable drag & drop, install it with:\n\n"
            "    pip install tkinterdnd2\n\n"
            "After installing, restart this program."
        )
    # Call after mainloop starts so it doesn't interrupt UI creation
    root.after(200, show_dnd_info)

root.mainloop()