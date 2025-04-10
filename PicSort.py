import os
import shutil
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk

# Configuration
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
KEEP_FOLDER = "kept_images"
DISCARD_FOLDER = "discarded_images"
RESIZED_FOLDER = "resized_images"

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

        self.back_btn = tk.Button(self.btn_frame, text="Go Back", command=self.go_back, width=10)
        self.back_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.keep_btn = tk.Button(self.btn_frame, text="Keep", command=self.keep_image, width=10)
        self.keep_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.keep_and_resize_btn = tk.Button(self.btn_frame, text="Keep & Resize", command=self.keep_and_resize_image, width=15)
        self.keep_and_resize_btn.pack(side=tk.LEFT, padx=10, pady=10)

        self.discard_btn = tk.Button(self.btn_frame, text="Discard", command=self.discard_image, width=10)
        self.discard_btn.pack(side=tk.RIGHT, padx=10, pady=10)

        self.select_folder_btn = tk.Button(root, text="Select Folder", command=select_folder)
        self.select_folder_btn.pack()

        ensure_folder_exists(KEEP_FOLDER)
        ensure_folder_exists(DISCARD_FOLDER)
        ensure_folder_exists(RESIZED_FOLDER)

    def load_images(self, folder):
        kept_images = {os.path.basename(f) for f in os.listdir(KEEP_FOLDER)}
        discarded_images = {os.path.basename(f) for f in os.listdir(DISCARD_FOLDER)}

        self.image_list = [os.path.join(folder, f) for f in os.listdir(folder)
                           if os.path.splitext(f)[1].lower() in IMAGE_EXTENSIONS
                           and f not in kept_images
                           and f not in discarded_images]
        self.current_index = 0
        self.show_image()

    def show_image(self):
        if self.current_index < len(self.image_list):
            image_path = self.image_list[self.current_index]
            image = Image.open(image_path)
            image = image.resize((800, 600), Image.Resampling.LANCZOS)  # Updated here
            self.photo = ImageTk.PhotoImage(image)
            self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
            self.label.config(text=f"Image {self.current_index + 1} of {len(self.image_list)}")
        else:
            self.label.config(text="No more images to sort.")
            self.canvas.delete("all")

    def go_back(self):
        if self.current_index > 0:
            self.current_index -= 1
            self.show_image()

    def keep_image(self):
        if self.current_index < len(self.image_list):
            image_path = self.image_list[self.current_index]
            shutil.move(image_path, os.path.join(KEEP_FOLDER, os.path.basename(image_path)))
            self.image_list.pop(self.current_index)
            self.show_image()

    def keep_and_resize_image(self):
        if self.current_index < len(self.image_list):
            image_path = self.image_list[self.current_index]
            shutil.move(image_path, os.path.join(KEEP_FOLDER, os.path.basename(image_path)))
            self.resize_for_sms(os.path.join(KEEP_FOLDER, os.path.basename(image_path)), RESIZED_FOLDER)
            self.image_list.pop(self.current_index)
            self.show_image()

    def resize_for_sms(self, input_path, output_folder, max_size=(1024, 1024), quality=85):
        os.makedirs(output_folder, exist_ok=True)
        filename = os.path.basename(input_path)
        img = Image.open(input_path)
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")
        img.convert("RGB").save(output_path, "JPEG", quality=quality)

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

