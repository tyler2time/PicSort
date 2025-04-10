from PIL import Image
import os

input_folder = r"C:\Fooocus_win64_2-5-0_2\Fooocus\outputs\ToBeResized"
output_folder = r"C:\Fooocus_win64_2-5-0_2\Fooocus\outputs\Resized"
max_size = (1024, 1024)  # SMS-friendly size
quality = 85  # Adjust 60–90 for file size vs quality

os.makedirs(output_folder, exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
        img_path = os.path.join(input_folder, filename)
        img = Image.open(img_path)

        # Updated to use Image.Resampling.LANCZOS
        img.thumbnail(max_size, Image.Resampling.LANCZOS)  # Keeps aspect ratio

        output_path = os.path.join(output_folder, os.path.splitext(filename)[0] + ".jpg")
        img.convert("RGB").save(output_path, "JPEG", quality=quality)

print("Resizing complete.")
