import os
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Configuration
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
KEEP_FOLDER = "kept_images"
DISCARD_FOLDER = "discarded_images"

def select_folder():
    folder = filedialog.askdirectory()
    if folder:
        app.load_images(folder)

def ensure_folder_exists(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

class ImageSorterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Sorter")
        self.image_list = []
        self.current_index = 0

        self.label = tk.Label(root, text="Select a folder to start sorting.")
        self.label.pack()

        self.canvas = tk.Canvas(root, width=800, height=600)
        self.canvas.pack()

        self.btn_frame = tk.Frame(root)
        self.btn_frame.pack()

        self.keep_btn = tk.Button(self.btn_frame, text="Keep", command=self.keep_image, width=10)
        self.keep_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.discard_btn = tk.Button(self.btn_frame, text="Discard", command=self.discard_image, width=10)
        self.discard_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        self.select_folder_btn = tk.Button(root, text="Select Folder", command=select_folder)
        self.select_folder_btn.pack()

        ensure_folder_exists(KEEP_FOLDER)
        ensure_folder_exists(DISCARD_FOLDER)

    def load_images(self, folder):
        self.image_list = [os.path.join(folder, f) for f in os.listdir(folder)
                           if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS]
        self.current_index = 0
        self.show_image()

    def show_image(self):
        if self.current_index < len(self.image_list):
            image_path = self.image_list[self.current_index]
            image = Image.open(image_path)
            image = image.resize((800, 600), Image.ANTIALIAS)
            self.tk_image = ImageTk.PhotoImage(image)
            self.canvas.create_image(400, 300, anchor=tk.CENTER, image=self.tk_image)
            self.label.config(text=f"Viewing {os.path.basename(image_path)} ({self.current_index + 1}/{len(self.image_list)})")
        else:
            self.label.config(text="All images sorted!")
            self.canvas.delete("all")

    def keep_image(self):
        self.current_index += 1
        self.show_image()

    def discard_image(self):
        if self.current_index < len(self.image_list):
            image_path = self.image_list[self.current_index]
            shutil.move(image_path, os.path.join(DISCARD_FOLDER, os.path.basename(image_path)))
            self.image_list.pop(self.current_index)
            self.show_image()

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageSorterApp(root)
    root.mainloop()
