import requests
import time
from gradio_client import Client, handle_file

stability_key = "sk-CJJTIPiDSzoHR6pmvWLbJZ5026rZI2RGqWiujNl3uB71wzbP"

print("1. Generating base human model with Stability AI...")
response = requests.post(
    "https://api.stability.ai/v2beta/stable-image/generate/core",
    headers={
        "authorization": f"Bearer {stability_key}",
        "accept": "image/*"
    },
    files={"none": ''},
    data={
        "prompt": "A fierce male heavy metal musician with long hair wearing a plain black t-shirt, passionately singing on a concert stage, red lasers, dark atmosphere, photorealistic, sharp focus",
        "output_format": "jpeg",
        "aspect_ratio": "1:1"
    },
)

if response.status_code == 200:
    with open("base_human.jpg", "wb") as f:
        f.write(response.content)
    print("Base human saved as base_human.jpg")
else:
    print("Stability AI Error:", response.json())
    exit()

print("2. Sending to IDM-VTON for Virtual Try-On...")
client = Client("yisol/IDM-VTON")

# The inputs for yisol/IDM-VTON:
# fn_index=1 typically is the main try-on function. Let's use the API properly.
try:
    result = client.predict(
        dict({"background":handle_file('base_human.jpg'),"layers":[],"composite":None}),
        handle_file('assets/images/66115efe9c49a090f3094ea1/img_0.jpg'),
        "Short Sleeve T-Shirt",
        True,  # is_checked (auto-crop)
        True,  # is_checked_crop
        30,    # denoise_steps
        42,    # seed
        api_name="/tryon"
    )
    print("VTON Success! Result path:", result)
    
    # Copy the result to our folder
    import shutil
    shutil.copy(result[0], "final_vton.jpg")
    print("Saved final VTON to final_vton.jpg")
except Exception as e:
    print("VTON Error:", e)
