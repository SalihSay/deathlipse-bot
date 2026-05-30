import requests
import io
import rembg
from PIL import Image

api_key = "sk-CJJTIPiDSzoHR6pmvWLbJZ5026rZI2RGqWiujNl3uB71wzbP"
url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"

# We use a Printify Model Photo (e.g. img_4.jpg from the first t-shirt which was a model)
image_path = "assets/images/65d0f3f11888388ea400cc1b/img_4.jpg" 
# or 66115efe9c49a090f3094ea1/img_4.jpg which might be a model

with open(image_path, "rb") as f:
    input_data = f.read()

# Remove background to create the mask
output_data = rembg.remove(input_data)
with open("temp_model_transparent.png", "wb") as f:
    f.write(output_data)

prompt = "A massive heavy metal concert stage in the background. Vibrant piercing red laser lights cutting through thick atmospheric fog. Epic rock and roll atmosphere, photorealistic, cinematic lighting matching the subject"

try:
    with open("temp_model_transparent.png", "rb") as img_file:
        response = requests.post(
            url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Accept": "image/*"
            },
            files={
                "image": img_file
            },
            data={
                "prompt": prompt,
                "output_format": "jpeg"
            },
            timeout=120
        )

    if response.status_code == 200:
        with open("test_poster_stability_model.jpg", 'wb') as file:
            file.write(response.content)
        print("Saved to test_poster_stability_model.jpg")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception: {e}")
