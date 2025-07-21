import os
import glob
import tkinter as tk
from tkinter import filedialog, simpledialog, ttk, messagebox
from PIL import Image


def resize_image(path, output_folder, target_size, keep_aspect, crop_to_fit):
    try:
        with Image.open(path) as img:
            if crop_to_fit:
                img = resize_and_crop(img, target_size)
            elif keep_aspect:
                img.thumbnail(target_size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(target_size, Image.Resampling.LANCZOS)

            base = os.path.basename(path)
            name, ext = os.path.splitext(base)
            output_path = os.path.join(output_folder, f"{name}_resized{ext}")
            img.save(output_path)
            return output_path
    except Exception as e:
        print(f"Failed to resize {path}: {e}")
        return None


def process_images(input_folder, output_folder, target_size, keep_aspect, progress_bar):
    image_paths = glob.glob(os.path.join(input_folder, "*.*"))
    image_paths = [p for p in image_paths if p.lower().endswith((".jpg", ".jpeg", ".png", ".bmp", ".gif"))]

    total = len(image_paths)
    for i, path in enumerate(image_paths, start=1):
        resize_image(path, output_folder, target_size, keep_aspect, crop_var.get())
        progress_bar["value"] = (i / total) * 100
        root.update_idletasks()

    messagebox.showinfo("Done", f"Resized {total} images!")


def start_resize():
    messagebox.showinfo("Select Image Folder", "Select a folder that contains the images you want to resize.")

    input_folder = filedialog.askdirectory(title="Select Input Folder")
    if not input_folder:
        return

    messagebox.showinfo("Select Output Folder", "Select a folder where the resized images will be saved.")

    output_folder = filedialog.askdirectory(title="Select Output Folder")
    if not output_folder:
        return

    width = simpledialog.askinteger("Resize", "Enter new width:")
    height = simpledialog.askinteger("Resize", "Enter new height:")
    if not width or not height:
        return

    keep_aspect = aspect_var.get()
    size = (width, height)
    progress_bar["value"] = 0
    process_images(input_folder, output_folder, size, keep_aspect, progress_bar)


def start_resize_selected():
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

    width = simpledialog.askinteger("Resize", "Enter new width:")
    height = simpledialog.askinteger("Resize", "Enter new height:")
    if not width or not height:
        return

    size = (width, height)
    keep_aspect = aspect_var.get()

    total = len(file_paths)
    for i, path in enumerate(file_paths, start=1):
        resize_image(path, output_folder, size, keep_aspect, crop_var.get())
        progress_bar["value"] = (i / total) * 100
        root.update_idletasks()

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


root = tk.Tk()
root.title("Batch Image Resizer")
root.geometry("400x300")

frame = tk.Frame(root)
frame.pack(pady=20)

aspect_var = tk.BooleanVar()
aspect_check = tk.Checkbutton(frame, text="Keep Aspect Ratio", variable=aspect_var)
aspect_check.grid(row=0, column=0, columnspan=2, pady=10)

crop_var = tk.BooleanVar()
crop_check = tk.Checkbutton(frame, text="Crop to Fit", variable=crop_var)
crop_check.grid(row=1, column=0, columnspan=2, pady=10)

start_button = tk.Button(frame, text="Start Batch Resize", command=start_resize)
start_button.grid(row=2, column=0, columnspan=2, pady=10)

select_button = tk.Button(frame, text="Resize Selected Images", command=start_resize_selected)
select_button.grid(row=3, column=0, columnspan=2, pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()

