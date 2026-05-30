import os
import csv
import glob
import random
from moviepy.editor import ImageClip, AudioFileClip, VideoFileClip

CSV_FILE = "bulk_schedule.csv"
IMG_DIR = "bulk_images"
OUT_DIR = "reels_output"
AUDIO_DIR = "assets/audio"

def ensure_dirs():
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(AUDIO_DIR, exist_ok=True)

def add_audio_to_silent_video(video_path):
    audios = glob.glob(f"{AUDIO_DIR}/*.mp3")
    if not audios:
        print(f"⚠️ Müzik Eklenemedi: {AUDIO_DIR} klasörüne en az bir .mp3 müzik dosyası koymalısınız!")
        return False
        
    try:
        video_clip = VideoFileClip(video_path)
        
        # Zaten ses varsa işlem yapma
        if video_clip.audio is not None:
            video_clip.close()
            return True
            
        print(f"🎵 Sessiz videoya müzik ekleniyor: {video_path}")
        random_audio = random.choice(audios)
        audio_clip = AudioFileClip(random_audio).set_duration(video_clip.duration)
        audio_clip = audio_clip.audio_fadeout(2)
        
        video_with_audio = video_clip.set_audio(audio_clip)
        
        temp_output = video_path.replace(".mp4", "_temp.mp4")
        video_with_audio.write_videofile(
            temp_output,
            fps=24,
            codec="libx264",
            audio_codec="aac",
            threads=4,
            logger=None
        )
        
        video_clip.close()
        audio_clip.close()
        
        if os.path.exists(temp_output):
            os.replace(temp_output, video_path)
            print(f"✅ Müzik başarıyla birleştirildi: {video_path}")
            return True
    except Exception as e:
        print(f"❌ Müzik ekleme hatası: {e}")
    return False

def generate_video_from_image(image_path, output_path):
    print(f"🎬 Görselden video üretiliyor: {image_path}")
    clip = ImageClip(image_path).set_duration(7)
    
    # Ken Burns Zoom Efekti
    def zoom_effect(t):
        return 1 + 0.05 * t
        
    clip = clip.resize(zoom_effect)
    clip = clip.set_position(('center', 'center'))
    
    audios = glob.glob(f"{AUDIO_DIR}/*.mp3")
    if audios:
        random_audio = random.choice(audios)
        audio_clip = AudioFileClip(random_audio).set_duration(clip.duration)
        audio_clip = audio_clip.audio_fadeout(2)
        clip = clip.set_audio(audio_clip)
        
    clip.write_videofile(
        output_path, 
        fps=24, 
        codec="libx264", 
        audio_codec="aac",
        threads=4,
        logger=None
    )
    print(f"✅ Video başarıyla kaydedildi: {output_path}")

def process_csv():
    ensure_dirs()
    
    if not os.path.exists(CSV_FILE):
        print("bulk_schedule.csv bulunamadı!")
        return
        
    with open(CSV_FILE, "r", encoding="utf-8") as f:
        reader = list(csv.reader(f))
        
    if len(reader) <= 1:
        print("CSV dosyasında veri yok!")
        return
        
    updated_rows = [reader[0]] # header
    
    for row in reader[1:]:
        # Eğer bu satır 6 kolonlu ise ve Video_File alanı dolu ise
        if len(row) >= 6 and row[3] and ".mp4" in row[3]:
            vid_filename = row[3]
            vid_path = os.path.join(OUT_DIR, vid_filename)
            
            if os.path.exists(vid_path):
                # Bu videoya müzik eklemeyi dene (eğer ses yoksa ekler)
                add_audio_to_silent_video(vid_path)
            updated_rows.append(row)
            
        # Eğer bu satır 3 kolonlu ise (Text, Image_File, URL)
        elif len(row) == 3 or (len(row) >= 5 and not row[3]):
            text = row[0]
            img_file = row[1] if len(row) == 3 else row[2]
            url = row[2] if len(row) == 3 else row[4]
            
            pin_text = text
            img_path = os.path.join(IMG_DIR, img_file)
            vid_filename = img_file.replace(".jpg", ".mp4").replace(".png", ".mp4")
            vid_path = os.path.join(OUT_DIR, vid_filename)
            
            if os.path.exists(img_path):
                if not os.path.exists(vid_path):
                    try:
                        generate_video_from_image(img_path, vid_path)
                    except Exception as e:
                        print(f"Hata oluştu: {e}")
                        vid_filename = ""
                
                # 6 Kolonlu Formata Dönüştür
                # Format: IG_TikTok_Text, Pinterest_Text, Image_File, Video_File, Product_URL, Status
                new_row = [text, pin_text, img_file, vid_filename, url, "PENDING"]
                updated_rows.append(new_row)
            else:
                updated_rows.append(row)
        else:
            updated_rows.append(row)
            
    with open(CSV_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(updated_rows)
        
    print("\n🎉 Tüm video üretim işlemleri tamamlandı ve liste güncellendi!")

if __name__ == "__main__":
    try:
        import moviepy
    except ImportError:
        print("HATA: moviepy kütüphanesi eksik. Lütfen terminale şunu yazın:")
        print("pip install moviepy==1.0.3")
        import sys
        sys.exit(1)
        
    process_csv()
