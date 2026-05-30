import requests
import io
import base64
from PIL import Image

api_key = "sk-CJJTIPiDSzoHR6pmvWLbJZ5026rZI2RGqWiujNl3uB71wzbP"
url = "https://api.stability.ai/v2beta/stable-image/edit/inpaint"

# Use the already processed image where model is opaque and background is transparent
transparent_img_path = "model_nobg.png"

prompt = "dark black background, heavy metal concert stage with red laser beams, thick fog and smoke machines, massive Marshall amplifiers stacked high, dramatic red and purple spotlights, epic dark arena, no yellow, photorealistic concert photography"

print("Sending transparent image to Stability AI inpainting API...")

try:
    with open(transparent_img_path, "rb") as img_file:
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
                "output_format": "png",
                # The alpha channel determines the mask (transparent = replace)
            },
            timeout=120
        )

    if response.status_code == 200:
        print("Success! Saving image...")
        with open("test_poster_stability_inpaint.png", 'wb') as file:
            file.write(response.content)
        print("Saved to test_poster_stability_inpaint.png")
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
except Exception as e:
    print(f"Exception: {e}")
