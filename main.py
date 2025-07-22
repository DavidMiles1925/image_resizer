import os
import glob
import tkinter as tk
from tkinter import filedialog, simpledialog, ttk, messagebox
from PIL import Image
from PIL import ImageEnhance


def resize_image(path, output_folder, target_size, keep_aspect, crop_to_fit, brightness_enhance, suffix):
    try:

        with Image.open(path) as img:
            if brightness_enhance:
                enhancer = ImageEnhance.Brightness(img)
                img = enhancer.enhance(1.2)

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
    for i, path in enumerate(image_paths, start=1):
        filename_label.config(text=os.path.basename(path))  # Update label
        resize_image(path, output_folder, target_size, keep_aspect, crop_var.get(), brightness_var.get(), suffix_entry.get())
        progress_bar["value"] = (i / total) * 100
        root.update_idletasks()

    filename_label.config(text="All done!")  # Reset text
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
    process_images(input_folder, output_folder, size, keep_aspect, progress_bar, filename_label)

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


root = tk.Tk()
root.title("Batch Image Resizer v1.2")
root.iconbitmap("resize.ico")
root.geometry("400x350")

frame = tk.Frame(root)
frame.pack(pady=20)

bright_label = tk.Label(frame, text="Increase Brightness?", font=("Arial", 10, "bold"))
bright_label.grid(row=0, column=0, columnspan=2, pady=5)

brightness_var = tk.BooleanVar()
brightness_check = tk.Checkbutton(frame, text="Increase brightness 20%", variable=brightness_var)
brightness_check.grid(row=0, column=2, columnspan=2, pady=5)

choice_label = tk.Label(frame, text="Select up to ONE:", font=("Arial", 10, "bold"))
choice_label.grid(row=1, column=1, columnspan=2, pady=5)

aspect_var = tk.BooleanVar()
aspect_check = tk.Checkbutton(frame, text="Keep Aspect Ratio", variable=aspect_var)
aspect_check.grid(row=2, column=0, columnspan=2, pady=5)

crop_var = tk.BooleanVar()
crop_check = tk.Checkbutton(frame, text="Crop to Fit", variable=crop_var)
crop_check.grid(row=2, column=2, columnspan=2, pady=5)

suffix_label = tk.Label(frame, text="Filename suffix:", font=("Arial", 10, "bold"))
suffix_label.grid(row=3, column=1, columnspan=2, pady=5)
suffix_entry = tk.Entry(frame)
suffix_entry.insert(0, "_resized")  # Default value
suffix_entry.grid(row=3, column=3, columnspan=2, pady=5)

button_label = tk.Label(frame, text="Resize folder or files(s)?", font=("Arial", 10, "bold"))
button_label.grid(row=4, column=1, columnspan=2, pady=5)

start_button = tk.Button(frame, text="Start Batch (Folder) Resize", command=start_resize)
start_button.grid(row=5, column=0, columnspan=2, pady=5)

select_button = tk.Button(frame, text="Resize Only Selected Images", command=start_resize_selected)
select_button.grid(row=5, column=2, columnspan=2, pady=5)

filename_label = tk.Label(root, text="Ready", font=("Arial", 10))
filename_label.pack(pady=5)

progress_bar = ttk.Progressbar(root, orient="horizontal", length=300, mode="determinate")
progress_bar.pack(pady=10)

root.mainloop()

