import requests
from PIL import Image
import io

def main():
    print("--- STEP 1: Generating Epic Metalhead Model ---")
    prompt = "a badass heavy metal musician with long black hair, tattoos, wearing a PLAIN BLACK T-SHIRT (no logos, no graphics, completely blank), performing on a dark stage with red laser lights, epic photorealistic concert photography, 8k"
    encoded_prompt = requests.utils.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=1024&height=1024&model=flux-realism&nologo=true"
    
    resp = requests.get(url, timeout=60)
    if resp.status_code == 200:
        with open("generated_metalhead_blank.jpg", "wb") as f:
            f.write(resp.content)
        print("Generated model saved.")
    else:
        print("Failed to generate model.")
        return

    print("\n--- STEP 2: Compositing Raw Print onto the Model ---")
    # Open the generated model
    model_img = Image.open("generated_metalhead_blank.jpg").convert("RGBA")
    
    # Open the raw design
    design_img = Image.open("raw_design.png").convert("RGBA")
    
    # The design is 500x500. We might need to scale it to fit nicely on the chest.
    # For a 1024x1024 image, the chest is roughly in the middle. Let's make it 300x300.
    target_width = 300
    ratio = target_width / design_img.width
    target_height = int(design_img.height * ratio)
    design_resized = design_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Let's find a reasonable chest position. Usually around (width/2 - target_width/2, height/2 - target_height/2 - 50)
    pos_x = (1024 - target_width) // 2
    pos_y = (1024 - target_height) // 2 + 50 # slightly lower than dead center
    
    # Create a blank layer the same size as the model
    design_layer = Image.new("RGBA", model_img.size, (0, 0, 0, 0))
    design_layer.paste(design_resized, (pos_x, pos_y), mask=design_resized)
    
    # Optional: Apply a slight rotation to match a dynamic pose, but usually they face forward.
    # Let's just do a direct alpha composite first.
    final_img = Image.alpha_composite(model_img, design_layer)
    
    final_img.convert("RGB").save("mockup_option_d.jpg", quality=95)
    print("SUCCESS! Saved to mockup_option_d.jpg")

if __name__ == "__main__":
    main()
