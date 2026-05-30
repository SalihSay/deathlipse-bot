import os
import requests
from PIL import Image

def main():
    print("--- STEP 1: Fetching Concert Background from Pollinations ---")
    prompt = "dark black background, heavy metal concert stage with red laser beams, thick fog and smoke machines, massive Marshall amplifiers stacked high, dramatic red and purple spotlights, epic dark arena, photorealistic concert photography"
    encoded_prompt = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux-realism&nologo=true"
    
    resp = requests.get(url, timeout=60)
    if resp.status_code == 200:
        with open("pollinations_bg.jpg", "wb") as f:
            f.write(resp.content)
        print("Background downloaded successfully.")
    else:
        print("Failed to download background.")
        return

    print("\n--- STEP 2: Compositing Model onto Background ---")
    # Open the generated background
    bg = Image.open("pollinations_bg.jpg").convert("RGBA")
    
    # Open the model with transparent background
    model = Image.open("model_nobg.png").convert("RGBA")
    
    # Resize model to match background if necessary
    model = model.resize((1024, 1024), Image.Resampling.LANCZOS)
    
    # Composite: Paste the model onto the background using the model's alpha channel as mask
    bg.paste(model, (0, 0), mask=model)
    
    # Convert back to RGB to save as JPG
    final_img = bg.convert("RGB")
    final_img.save("final_composite_model.jpg", quality=95)
    print("\nSUCCESS! Final image saved to final_composite_model.jpg")

if __name__ == "__main__":
    main()
