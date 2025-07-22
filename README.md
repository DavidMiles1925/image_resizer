# Batch Image Resizer

A simple Python GUI application to batch resize images with options to keep aspect ratio or crop-to-fit. It supports resizing either an entire folder of images or selecting individual image files.

---

## Features

- Resize images to any specified width and height.
- Option to **increase brightness** by 20% (v1.1)
- Option to **keep aspect ratio** (resize to fit within target size without distortion).
- Option to **crop-to-fit** (resize and crop images to exactly fill the target size).
- Option to **edit file suffix**. (v1.2)
- Resize all images in a folder or select specific image files.
- Progress bar to track batch resizing progress.
- Display current working filename above the progress bar. (v1.2)
- Supports common image formats: JPG, JPEG, PNG, BMP, GIF.
- User-friendly dialogs guide you through each step.

---

## Windows Installation

From the `/dist` folder above, download and run the file `main.exe`.

---

## Python Installation

### Requirements

- Python 3.7 or later
- [Pillow](https://python-pillow.org/) (Python Imaging Library fork)
- Standard Python libraries: `tkinter` (usually included with Python)

### Procedure

1. Clone this repository or download the script file.

2. Install Pillow if you don't have it:

```bash
pip install pillow
```

3. Run the program from the command line.

```bash
python main.py
```

---

## Distribution Notes

Windows package was made with pyinstaller

````bash
pip install pyinstaller
pyinstaller --onefile --windowed --add-data "resize.ico;." main.py```
````
