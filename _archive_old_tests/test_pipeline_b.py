import requests
import random
import urllib.parse
from gradio_client import Client, handle_file
from PIL import Image
import shutil
import os
from dotenv import load_dotenv

load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN:
    os.environ["HF_TOKEN"] = HF_TOKEN

def get_pollinations_image(prompt, filename, width=1024, height=1024):
    seed = random.randint(1, 100000)
    encoded_prompt = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&model=flux-realism&seed={seed}&nologo=true"
    print(f"Fetching from Pollinations...")
    res = requests.get(url, timeout=60)
    if res.status_code == 200:
        with open(filename, "wb") as f:
            f.write(res.content)
        return True
    else:
        print(f"Error {res.status_code}: {res.text}")
        return False

def main():
    # Step 1: Metal Model
    print("\n--- STEP 1: Generating Base Metal Model ---")
    model_prompt = "heavy metal musician full body pale skin long black hair dramatic stage lighting photorealistic, blank t-shirt, standing straight, simple background"
    get_pollinations_image(model_prompt, "pipeline_b_model.jpg", width=768, height=1024)

    # Step 2: IDM-VTON
    print("\n--- STEP 2: IDM-VTON (Virtual Try-On) ---")
    flat_tshirt = "assets/images/66115efe9c49a090f3094ea1/img_0.jpg"
    vton_client = Client("yisol/IDM-VTON")
    result_vton = vton_client.predict(
        dict({"background":handle_file("pipeline_b_model.jpg"),"layers":[],"composite":None}),
        handle_file(flat_tshirt),
        "Short Sleeve T-Shirt",
        True,
        True,
        30,
        42,
        api_name="/tryon"
    )
    shutil.copy(result_vton[0], "pipeline_b_vton.png")
    print("VTON Output saved to pipeline_b_vton.png")

    # Step 3: BRIA-RMBG-2.0
    print("\n--- STEP 3: Background Removal (BRIA) ---")
    bria_client = Client("briaai/BRIA-RMBG-2.0")
    try:
        # Check standard endpoint
        result_bria = bria_client.predict(
            image=handle_file("pipeline_b_vton.png"),
            api_name="/image"
        )
        # BRIA returns (SliderData, output_png_file)
        bria_path = result_bria[1]
        shutil.copy(bria_path, "pipeline_b_model_nobg.png")
        print("Model no-bg saved to pipeline_b_model_nobg.png")
    except Exception as e:
        print("Error with BRIA process endpoint. Exception:", e)

    # Step 4: Metal Background
    print("\n--- STEP 4: Generating Concert Background ---")
    bg_prompt = "dark metal concert stage dramatic smoke fog red spotlights, crowd silhouette, 8k resolution, cinematic lighting"
    get_pollinations_image(bg_prompt, "pipeline_b_bg.jpg", width=1080, height=1080)

    # Step 5: Composite
    print("\n--- STEP 5: Compositing Final Image ---")
    bg = Image.open("pipeline_b_bg.jpg").convert("RGBA")
    model = Image.open("pipeline_b_model_nobg.png").convert("RGBA")
    
    # Resize model slightly if it's bigger than background, or just center bottom
    # Model is 768x1024. Background is 1080x1080.
    x_offset = (bg.width - model.width) // 2
    y_offset = bg.height - model.height
    
    bg.alpha_composite(model, (x_offset, max(0, y_offset)))
    bg.convert("RGB").save("pipeline_b_final.jpg")
    print("Pipeline B Complete! Final image saved to pipeline_b_final.jpg")

if __name__ == "__main__":
    main()
