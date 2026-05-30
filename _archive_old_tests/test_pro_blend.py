import requests
from PIL import Image, ImageChops, ImageEnhance
import io

def main():
    print("--- Testing Professional Blending ---")
    
    # 1. Open the background (generated metalhead)
    bg = Image.open("mockup_realistic_tshirt.jpg").convert("RGBA")
    
    # Let's actually use the generated metalhead front without the logo first
    # Wait, mockup_realistic_tshirt.jpg already has the logo pasted. 
    # Let's use generated_metalhead_front.jpg
    model_img = Image.open("generated_metalhead_front.jpg").convert("RGBA")
    
    # 2. Open the raw design
    design_img = Image.open("raw_design.png").convert("RGBA")
    
    # Resize
    target_width = 220
    ratio = target_width / design_img.width
    target_height = int(design_img.height * ratio)
    design_resized = design_img.resize((target_width, target_height), Image.Resampling.LANCZOS)
    
    # Position
    pos_x = 340
    pos_y = 280
    
    # Create a transparent layer with the logo in position
    logo_layer = Image.new("RGBA", model_img.size, (0, 0, 0, 0))
    logo_layer.paste(design_resized, (pos_x, pos_y), mask=design_resized)
    
    # --- PROFESSIONAL BLENDING SIMULATION ---
    # In Photoshop, to make a print look real on a dark shirt, you use "Screen" or "Lighten" for light colors,
    # or you blend the shirt's lighting over the logo.
    # Let's extract the luminosity of the shirt where the logo is.
    shirt_crop = model_img.crop((pos_x, pos_y, pos_x+target_width, pos_y+target_height)).convert("L")
    
    # We want the shadows of the shirt to darken the logo, and the highlights to lighten it.
    # A simple way in PIL is to multiply the logo by the shirt's luminosity.
    shirt_crop_rgba = shirt_crop.convert("RGBA")
    
    # We create an image that is the logo, but its RGB values are multiplied by the shirt's grayscale values
    blended_logo = ImageChops.multiply(design_resized, shirt_crop_rgba)
    
    # Put the original alpha back
    blended_logo.putalpha(design_resized.split()[3])
    
    # Reduce opacity to 90% so it sinks into the fabric
    alpha = blended_logo.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(0.9)
    blended_logo.putalpha(alpha)
    
    # Create final layer
    final_layer = Image.new("RGBA", model_img.size, (0, 0, 0, 0))
    final_layer.paste(blended_logo, (pos_x, pos_y), mask=blended_logo)
    
    # Composite
    final_img = Image.alpha_composite(model_img, final_layer)
    
    final_img.convert("RGB").save("mockup_pro_blend.jpg", quality=95)
    print("Saved to mockup_pro_blend.jpg")

if __name__ == "__main__":
    main()
