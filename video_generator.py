import cv2
import numpy as np
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip
import os
import random

def create_blur_background(img, target_w=1080, target_h=1920):
    """Resmi 9:16 oranına sığdırır. Boşlukları blurlu arkaplan ile doldurur."""
    h, w = img.shape[:2]
    
    # Arkaplan için resmi target_h veya target_w'ye göre dolduracak şekilde büyüt
    scale_bg = max(target_w / w, target_h / h)
    bg_w, bg_h = int(w * scale_bg), int(h * scale_bg)
    bg_resized = cv2.resize(img, (bg_w, bg_h))
    
    # Merkezden kırp
    start_y = (bg_h - target_h) // 2
    start_x = (bg_w - target_w) // 2
    bg_cropped = bg_resized[start_y:start_y+target_h, start_x:start_x+target_w]
    
    # Ağır blur uygula
    bg_blurred = cv2.GaussianBlur(bg_cropped, (101, 101), 0)
    
    # Orijinal resmi target_w'ye sığacak şekilde küçült
    scale_fg = target_w / w
    fg_w, fg_h = int(w * scale_fg), int(h * scale_fg)
    fg_resized = cv2.resize(img, (fg_w, fg_h))
    
    # Orijinal resmi blurlu arkaplanın ortasına yerleştir
    canvas = bg_blurred.copy()
    y_offset = (target_h - fg_h) // 2
    
    if y_offset > 0:
        canvas[y_offset:y_offset+fg_h, 0:target_w] = fg_resized
    else:
        # Eğer fg uzunsa, fg'yi kırpıp yerleştir
        crop_y = -y_offset
        canvas[0:target_h, 0:target_w] = fg_resized[crop_y:crop_y+target_h, 0:target_w]
        
    return canvas

def apply_vignette(img):
    """Köşeleri karartır (Dark Aesthetic)"""
    h, w = img.shape[:2]
    X_resultant_kernel = cv2.getGaussianKernel(w, w/2)
    Y_resultant_kernel = cv2.getGaussianKernel(h, h/2)
    kernel = Y_resultant_kernel * X_resultant_kernel.T
    mask = 255 * kernel / np.linalg.norm(kernel)
    mask = mask / np.max(mask)
    
    img_vignette = np.copy(img)
    for i in range(3):
        img_vignette[:,:,i] = img_vignette[:,:,i] * mask
    return img_vignette

def apply_rgb_shift(img, shift_x=15, shift_y=5):
    """RGB Glitch efekti (kırmızı ve mavi kanalları kaydırır)"""
    h, w = img.shape[:2]
    glitch_img = np.zeros_like(img)
    
    # B kanalını sola, R kanalını sağa kaydır (G aynı kalır)
    b, g, r = cv2.split(img)
    
    # R (Sağa kaydır)
    r_shifted = np.roll(r, shift_x, axis=1)
    r_shifted = np.roll(r_shifted, shift_y, axis=0)
    
    # B (Sola kaydır)
    b_shifted = np.roll(b, -shift_x, axis=1)
    b_shifted = np.roll(b_shifted, -shift_y, axis=0)
    
    glitch_img = cv2.merge([b_shifted, g, r_shifted])
    return glitch_img

def apply_scanlines(img):
    """Eski kaset (VHS) çizgileri ekler"""
    h, w = img.shape[:2]
    scanlines = np.zeros((h, w, 3), dtype=np.uint8)
    # Her 4 pikselde bir siyah çizgi
    scanlines[::4, :, :] = 30
    
    img_scanlines = cv2.subtract(img, scanlines)
    return img_scanlines

def generate_tiktok_video(image_path, output_path, duration=7.0, fps=30):
    print(f"[{os.path.basename(image_path)}] Processing video...")
    
    img = cv2.imread(image_path)
    if img is None:
        print(f"Error: Could not read image {image_path}")
        return False
        
    # RGB yap (OpenCV BGR kullanır)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    
    # Blur Padding ile 1080x1920 oluştur
    base_frame = create_blur_background(img, 1080, 1920)
    base_frame = apply_vignette(base_frame)
    
    # Biraz doygunluğu kıs (Dark Aesthetic)
    hsv = cv2.cvtColor(base_frame, cv2.COLOR_RGB2HSV).astype("float32")
    hsv[:,:,1] = hsv[:,:,1] * 0.85 # %15 desature
    hsv = np.clip(hsv, 0, 255).astype("uint8")
    base_frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2RGB)
    
    total_frames = int(duration * fps)
    frames = []
    
    h, w = base_frame.shape[:2]
    center_x, center_y = w // 2, h // 2
    
    # Animasyon ayarları
    zoom_start = 1.0
    zoom_end = 1.15
    
    # Glitch zamanlamaları (rastgele 3-4 an seç)
    glitch_moments = [random.randint(30, total_frames-30) for _ in range(3)]
    
    for i in range(total_frames):
        progress = i / float(total_frames)
        current_zoom = zoom_start + (zoom_end - zoom_start) * progress
        
        # Crop hesaplama (Ken Burns)
        crop_w = int(w / current_zoom)
        crop_h = int(h / current_zoom)
        
        x1 = max(0, center_x - crop_w // 2)
        y1 = max(0, center_y - crop_h // 2)
        x2 = min(w, x1 + crop_w)
        y2 = min(h, y1 + crop_h)
        
        frame_cropped = base_frame[y1:y2, x1:x2]
        frame_resized = cv2.resize(frame_cropped, (w, h), interpolation=cv2.INTER_LINEAR)
        
        # Scanlines (sabit)
        frame_styled = apply_scanlines(frame_resized)
        
        # Glitch efekti (sadece belirli framelerde 3-4 kare boyunca)
        is_glitch = False
        for gm in glitch_moments:
            if gm <= i <= gm + 3:
                is_glitch = True
                break
                
        if is_glitch:
            shift_x = random.randint(10, 25)
            shift_y = random.randint(2, 8)
            frame_styled = apply_rgb_shift(frame_styled, shift_x, shift_y)
            
        frames.append(frame_styled)
    
    print(f"[{os.path.basename(image_path)}] Rendering MP4 (Silent)...")
    clip = ImageSequenceClip(frames, fps=fps)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    clip.write_videofile(output_path, codec="libx264", audio=False, logger=None)
    
    print(f"[{os.path.basename(image_path)}] Success! Saved to {output_path}")
    return True

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generate TikTok video from static mockup")
    parser.add_argument("image_path", help="Path to input image")
    parser.add_argument("output_path", help="Path to output mp4")
    args = parser.parse_args()
    
    generate_tiktok_video(args.image_path, args.output_path)
