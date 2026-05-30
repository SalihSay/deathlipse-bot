import requests
from PIL import Image, ImageEnhance
import io

def main():
    print("--- Using existing Generated Metalhead Model ---")
    
    print("\n--- STEP 2: Compositing Raw Print onto the T-Shirt ---")
    # Open the generated model
    model_img = Image.open("generated_metalhead_front.jpg").convert("RGBA")
    
    # Open the raw design
    design_img = Image.open("raw_design.png").convert("RGBA")
    
    # The model's chest is higher up and slightly to the left.
    target_width = 220
    ratio = target_width / design_img.width
    target_height = int(design_img.height * ratio)
    design_resized = design_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Reduce opacity slightly to make it look printed rather than floating
    alpha = design_resized.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.9)
    design_resized.putalpha(alpha)
    
    # Position: Adjusting for the specific seed=42 image.
    pos_x = 340  # The center of his chest is around here
    pos_y = 280  # Below the necklaces

    
    # Create a blank layer
    design_layer = Image.new("RGBA", model_img.size, (0, 0, 0, 0))
    design_layer.paste(design_resized, (pos_x, pos_y), mask=design_resized)
    
    # Composite
    final_img = Image.alpha_composite(model_img, design_layer)
    
    final_img.convert("RGB").save("mockup_realistic_tshirt.jpg", quality=95)
    print("SUCCESS! Saved to mockup_realistic_tshirt.jpg")

if __name__ == "__main__":
    main()
