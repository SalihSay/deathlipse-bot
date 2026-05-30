import os
from pathlib import Path
import os
from pathlib import Path
from PIL import Image, ImageFilter
from rembg import remove

# Test Image Path
IMAGE_PATH = Path("assets/images/65d0f3f11888388ea400cc1b/img_0.jpg")
OUTPUT_PATH = Path("test_poster_result.jpg")

print("1. Pollinations.ai ile Arka Plan Uretiliyor (%100 Ucretsiz & Kotasiz)...")
import requests
import urllib.parse

prompt = "A cinematic dark volcanic rock pedestal in a misty cave, red neon lights glowing from the cracks, highly detailed, photorealistic, 8k, masterpiece"
encoded_prompt = urllib.parse.quote(prompt)
url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&nologo=true&model=flux"

resp = requests.get(url)
bg_path = "test_bg_generated.jpg"
with open(bg_path, "wb") as f:
    f.write(resp.content)
    
print(f"Arka plan basariyla uretildi: {bg_path}")

print("2. Urun Arka Plani Siliniyor (rembg)...")
with open(IMAGE_PATH, "rb") as f:
    input_image_data = f.read()
    
# Remove background
output_image_data = remove(input_image_data)

# Save temp transparent shirt
temp_shirt_path = "temp_shirt.png"
with open(temp_shirt_path, "wb") as f:
    f.write(output_image_data)
    
print("3. Urun ve Arka Plan Birlestiriliyor...")
bg_img = Image.open(bg_path).convert("RGBA")
shirt_img = Image.open(temp_shirt_path).convert("RGBA")

# Resize shirt to fit nicely on the background (e.g. 70% of background height)
target_height = int(bg_img.height * 0.7)
aspect_ratio = shirt_img.width / shirt_img.height
target_width = int(target_height * aspect_ratio)

shirt_img = shirt_img.resize((target_width, target_height), Image.Resampling.LANCZOS)

# Calculate position (center horizontal, slightly lower vertical)
x = (bg_img.width - target_width) // 2
y = (bg_img.height - target_height) // 2 + 50

# Add a drop shadow for realism
shadow = Image.new("RGBA", shirt_img.size, (0, 0, 0, 0))
shadow_data = shadow.load()
shirt_data = shirt_img.load()

# Create black silhouette
for i in range(shirt_img.width):
    for j in range(shirt_img.height):
        r, g, b, a = shirt_data[i, j]
        if a > 0:
            shadow_data[i, j] = (0, 0, 0, int(a * 0.6)) # 60% opacity shadow

# Blur the silhouette
shadow = shadow.filter(ImageFilter.GaussianBlur(radius=15))

# Paste shadow slightly offset
bg_img.paste(shadow, (x, y + 20), shadow)

# Paste shirt
bg_img.paste(shirt_img, (x, y), shirt_img)

# Save final result
final_img = bg_img.convert("RGB") # Convert back to RGB for JPEG
final_img.save(OUTPUT_PATH, "JPEG", quality=95)

print(f"!!! POSTER BASARIYLA OLUSTURULDU: {OUTPUT_PATH}")

# Clean up
if os.path.exists(temp_shirt_path):
    os.remove(temp_shirt_path)
