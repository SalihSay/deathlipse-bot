import os
import random
import glob
import cv2
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from moviepy.editor import ImageSequenceClip, AudioFileClip, CompositeAudioClip
import moviepy.audio.fx.all as afx

# ==========================================
# GÖRSEL EFEKTLER (OPENCV)
# ==========================================
def apply_scanlines(frame, intensity=30):
    overlay = frame.copy().astype(np.int16)
    overlay[::2, :] -= intensity
    return np.clip(overlay, 0, 255).astype(np.uint8)

def apply_rgb_shift(frame, shift_x=10, shift_y=5):
    h, w, _ = frame.shape
    M_red = np.float32([[1, 0, shift_x], [0, 1, shift_y]])
    M_blue = np.float32([[1, 0, -shift_x], [0, 1, -shift_y]])
    red_channel = cv2.warpAffine(frame[:,:,2], M_red, (w, h))
    blue_channel = cv2.warpAffine(frame[:,:,0], M_blue, (w, h))
    shifted = frame.copy()
    shifted[:,:,2] = red_channel
    shifted[:,:,0] = blue_channel
    return shifted

def apply_flash(frame, intensity=80):
    flash = np.ones(frame.shape, dtype="uint8") * intensity
    return cv2.add(frame, flash)

def apply_vignette(frame, intensity=1.0):
    h, w = frame.shape[:2]
    X, Y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h))
    d = np.sqrt(X**2 + Y**2)
    vignette = 1 - np.clip(d * intensity - 0.2, 0, 1)
    vignette = np.dstack([vignette]*3)
    return cv2.convertScaleAbs(frame * vignette)

def apply_blood_drip(frame, frame_idx):
    # Basit bir damlama efekti
    overlay = frame.copy()
    for i in range(4):
        x = int(frame.shape[1] * (0.2 + i*0.2))
        y_max = int((frame_idx * 15) * (1.0 + i*0.2))
        cv2.line(overlay, (x, 0), (x, y_max), (0, 0, 139), max(2, 5 - i))
        cv2.circle(overlay, (x, y_max), max(3, 6 - i), (0, 0, 139), -1)
    return cv2.addWeighted(overlay, 0.7, frame, 0.3, 0)

def apply_static_noise(frame):
    noise = np.random.randint(0, 256, frame.shape, dtype='uint8')
    return cv2.addWeighted(frame, 0.6, noise, 0.4, 0)

# ==========================================
# STORY & VIDEO GENERATÖR
# ==========================================

def overlay_image_alpha(img, img_overlay, x, y):
    """
    Overlays a transparent PNG (img_overlay) onto a background image (img) at position (x,y).
    Expects both images to be in BGR/BGRA format, but overlay must have 4 channels (BGRA).
    """
    if img_overlay.shape[2] != 4:
        # No alpha channel, just copy
        y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
        x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])
        y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
        x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)
        if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o: return img
        img[y1:y2, x1:x2] = img_overlay[y1o:y2o, x1o:x2o, :3]
        return img

    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return img

    alpha = img_overlay[y1o:y2o, x1o:x2o, 3] / 255.0
    alpha_inv = 1.0 - alpha

    for c in range(3):
        img[y1:y2, x1:x2, c] = (alpha * img_overlay[y1o:y2o, x1o:x2o, c] +
                                alpha_inv * img[y1:y2, x1:x2, c])
    return img

def create_dynamic_background(product_path, product_type):
    # Rastgele dark arkaplan seç
    bg_folder = f"assets/backgrounds/{product_type}"
    if not os.path.exists(bg_folder):
        bg_folder = "assets/backgrounds/default"
        os.makedirs(bg_folder, exist_ok=True)
    
    backgrounds = glob.glob(f"{bg_folder}/*.jpg") + glob.glob(f"{bg_folder}/*.png")
    
    bg_img = None
    if backgrounds:
        bg_path = random.choice(backgrounds)
        bg_img = cv2.imread(bg_path)
    
    if bg_img is None:
        # Fallback blur
        prod_img = cv2.imread(product_path)
        if prod_img is None:
            return np.zeros((1920, 1080, 3), dtype=np.uint8)
        bg_img = cv2.resize(prod_img, (1080, 1920))
        bg_img = cv2.GaussianBlur(bg_img, (99, 99), 0)
        bg_img = apply_vignette(bg_img, 1.5)
        
    return cv2.resize(bg_img, (1080, 1920), interpolation=cv2.INTER_LANCZOS4)

def generate_story_image(product_path, product_type, output_path="assets/story_temp.png"):
    w, h = 1080, 1920
    bg_frame = create_dynamic_background(product_path, product_type)
    bg_frame = apply_vignette(bg_frame, 1.2)
    
    # OpenCV ile Product yükle (Transparan PNG desteği)
    prod_img = cv2.imread(product_path, cv2.IMREAD_UNCHANGED)
    if prod_img is None:
        print(f"HATA: Story için ürün resmi bulunamadı {product_path}")
        return False
        
    pw, ph = prod_img.shape[1], prod_img.shape[0]
    target_pw = int(w * 0.7)
    target_ph = int((target_pw / pw) * ph)
    
    # Kaliteli boyutlandırma: Küçültme ise INTER_AREA, Büyütme ise INTER_CUBIC
    interp = cv2.INTER_AREA if target_pw < pw else cv2.INTER_CUBIC
    prod_resized = cv2.resize(prod_img, (target_pw, target_ph), interpolation=interp)
    
    # OpenCV Alpha Blending
    px = (w - target_pw) // 2
    py = int(h * 0.25)
    bg_frame = overlay_image_alpha(bg_frame, prod_resized, px, py)
    
    # PIL'e aktarmadan önce mutlaka BGR -> RGB çevrimi yap (Renk uzayı hatasını önler)
    bg_rgb = cv2.cvtColor(bg_frame, cv2.COLOR_BGR2RGB)
    bg_pil = Image.fromarray(bg_rgb).convert("RGBA")
    
    # Text
    draw = ImageDraw.Draw(bg_pil)
    try:
        font_main = ImageFont.truetype("assets/fonts/metal_hook.ttf", 100)
        font_sub = ImageFont.truetype("assets/fonts/metal_hook.ttf", 60)
    except:
        font_main = ImageFont.load_default()
        font_sub = ImageFont.load_default()
        
    # NEW DROP
    text1 = "NEW DROP 🖤"
    bbox = draw.textbbox((0,0), text1, font=font_main)
    tw = bbox[2] - bbox[0]
    draw.text(((w - tw)//2, int(h * 0.12)), text1, font=font_main, fill=(255, 255, 255), stroke_width=3, stroke_fill=(0,0,0))
    
    # Tap the link -> Link in Bio
    text2 = "Link in Bio! 🔗"
    bbox2 = draw.textbbox((0,0), text2, font=font_sub)
    tw2 = bbox2[2] - bbox2[0]
    draw.text(((w - tw2)//2, int(h * 0.85)), text2, font=font_sub, fill=(200, 200, 200), stroke_width=2, stroke_fill=(0,0,0))
    
    final_img = bg_pil.convert("RGB")
    final_img.save(output_path)
    return output_path

def apply_hook_text(pil_img, text, frame_idx, fps=30):
    if not text:
        return pil_img
        
    # Frame 0-45 (1.5s): tam
    # Frame 45-60 (1.5-2s): fade out
    if frame_idx >= 60:
        return pil_img
        
    opacity = 255
    if frame_idx > 45:
        opacity = int(255 * (1.0 - (frame_idx - 45) / 15.0))
        
    txt_layer = Image.new("RGBA", pil_img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt_layer)
    try:
        font = ImageFont.truetype("assets/fonts/metal_hook.ttf", 90)
    except:
        font = ImageFont.load_default()
        
    bbox = draw.textbbox((0,0), text, font=font)
    tw = bbox[2] - bbox[0]
    w, h = pil_img.size
    
    draw.text(((w - tw)//2, int(h * 0.15)), text, font=font, fill=(255, 255, 255, opacity), stroke_width=4, stroke_fill=(0,0,0,opacity))
    return Image.alpha_composite(pil_img, txt_layer)

def generate_tiktok_video(image_path, output_path, hook_text="", product_type="default", style=None):
    if not os.path.exists(image_path):
        print(f"ERROR: File not found {image_path}")
        return False

    w, h = 1080, 1920
    fps = 30
    duration = 5 # 5 saniye
    total_frames = fps * duration

    styles = ["dark_glitch", "clean_minimal", "pulse_flash", "cinematic_fade", "blood_drip", "static_noise_burst"]
    if not style or style not in styles:
        style = random.choice(styles)
    
    print(f"[{os.path.basename(image_path)}] Selected Style: {style}")
    
    bg_frame_base = create_dynamic_background(image_path, product_type)
    bg_h, bg_w = bg_frame_base.shape[:2]
    
    # Ürünü OpenCV ile transparan yükle
    prod_img = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
    if prod_img is None:
        return False
        
    ph, pw = prod_img.shape[:2]
    base_prod_w = int(w * 0.75)
    
    frames = []
    
    glitch_moments = [random.randint(30, total_frames-30) for _ in range(4)]
    flash_moments = [i for i in range(15, total_frames, 30)]
    static_moments = [random.randint(10, total_frames-10) for _ in range(3)]
    
    for i in range(total_frames):
        progress = i / float(total_frames)
        
        # Parallax background (slight opposite move)
        bg_scale = 1.05
        current_bg_w = int(w * bg_scale)
        current_bg_h = int(h * bg_scale)
        bg_offset_y = int((1.0 - progress) * (current_bg_h - h))
        
        bg_interp = cv2.INTER_AREA if current_bg_w < bg_w else cv2.INTER_CUBIC
        bg_resized = cv2.resize(bg_frame_base, (current_bg_w, current_bg_h), interpolation=bg_interp)
        frame_cv = bg_resized[bg_offset_y:bg_offset_y+h, 0:w].copy()
        
        # Independent Zoom (Product only zooms, BG static)
        prod_zoom = 1.0 + (0.15 * progress)
        current_pw = int(base_prod_w * prod_zoom)
        current_ph = int((current_pw / pw) * ph)
        
        prod_interp = cv2.INTER_AREA if current_pw < pw else cv2.INTER_CUBIC
        resized_prod = cv2.resize(prod_img, (current_pw, current_ph), interpolation=prod_interp)
        
        # OpenCV Background Effects
        if style == "dark_glitch":
            frame_cv = apply_vignette(frame_cv, 1.2)
            frame_cv = apply_scanlines(frame_cv, 20)
            if any(gm <= i <= gm + 3 for gm in glitch_moments):
                frame_cv = apply_rgb_shift(frame_cv, random.randint(15, 30), random.randint(5, 10))
                
        elif style == "pulse_flash":
            frame_cv = apply_vignette(frame_cv, 0.8)
            if any(fm <= i <= fm + 2 for fm in flash_moments):
                frame_cv = apply_flash(frame_cv, 60)
                frame_cv = apply_rgb_shift(frame_cv, 5, 0)
                
        elif style == "blood_drip":
            frame_cv = apply_vignette(frame_cv, 1.4)
            frame_cv = apply_blood_drip(frame_cv, i)
            
        elif style == "static_noise_burst":
            frame_cv = apply_vignette(frame_cv, 1.2)
            if any(sm <= i <= sm + 4 for sm in static_moments):
                frame_cv = apply_static_noise(frame_cv)
                
        elif style == "clean_minimal":
            pass # No heavy effects
            
        # Paste product with OpenCV Alpha Blending (AFTER background effects so product stays clean)
        px = (w - current_pw) // 2
        py = (h - current_ph) // 2
        frame_cv = overlay_image_alpha(frame_cv, resized_prod, px, py)
        
        # Whole-frame effects (like fade in/out)
        if style == "cinematic_fade":
            fade_in = min(1.0, i / 30.0)
            fade_out = min(1.0, (total_frames - i) / 30.0)
            opacity = min(fade_in, fade_out)
            frame_cv = cv2.convertScaleAbs(frame_cv, alpha=opacity, beta=0)
            frame_cv = apply_vignette(frame_cv, 1.5)
            
        # Renk uzayı hatasını (Mora/Maviye kayma) önlemek için MoviePy'a gitmeden önce BGR -> RGB çevrimi!
        frame_rgb = cv2.cvtColor(frame_cv, cv2.COLOR_BGR2RGB)
        
        # Text Overlay'i RGB üzerinden PIL ile yap
        if hook_text:
            pil_img = Image.fromarray(frame_rgb).convert("RGBA")
            pil_res = apply_hook_text(pil_img, hook_text, i, fps)
            frame_rgb = np.array(pil_res.convert("RGB"))
            
        frames.append(frame_rgb)
    
    print(f"[{os.path.basename(image_path)}] Rendering MP4 (8000k Bitrate)...")
    clip = ImageSequenceClip(frames, fps=fps)
    
    # ==========================
    # SES ENTEGRASYONU (AUDIO)
    # ==========================
    audio_map = {
        "dark_glitch": "heavy",
        "pulse_flash": "heavy",
        "blood_drip": "heavy",
        "static_noise_burst": "heavy",
        "cinematic_fade": "dark_ambient",
        "clean_minimal": "mid_tempo"
    }
    audio_cat = audio_map.get(style, "mid_tempo")
    audio_files = glob.glob(f"assets/audio/{audio_cat}/*.mp3") + glob.glob(f"assets/audio/{audio_cat}/*.wav") + glob.glob(f"assets/audio/{audio_cat}/*.webm") + glob.glob(f"assets/audio/{audio_cat}/*.m4a")
    
    if not audio_files:
        audio_files = glob.glob("assets/audio/*/*.mp3") + glob.glob("assets/audio/*/*.wav") + glob.glob("assets/audio/*/*.webm") + glob.glob("assets/audio/*/*.m4a")
        
    if audio_files:
        selected_audio = random.choice(audio_files)
        print(f"[{os.path.basename(image_path)}] Applying Audio: {selected_audio}")
        try:
            audioclip = AudioFileClip(selected_audio)
            # Eğer ses videodan kısaysa döngüye sok
            if audioclip.duration < duration:
                audioclip = afx.audio_loop(audioclip, duration=duration)
            else:
                audioclip = audioclip.subclip(0, duration)
                
            audioclip = audioclip.audio_fadein(0.5)
            audioclip = audioclip.audio_fadeout(1.0)
            
            clip = clip.set_audio(audioclip)
        except Exception as e:
            print(f"Audio Error: {e}")
    else:
        print(f"[{os.path.basename(image_path)}] WARNING: No audio found. Silent video.")
    
    dir_name = os.path.dirname(output_path)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)
    clip.write_videofile(output_path, codec="libx264", audio_codec="aac", bitrate="8000k", logger=None)
    print(f"[{os.path.basename(image_path)}] Success! Saved to {output_path}")
    return True
