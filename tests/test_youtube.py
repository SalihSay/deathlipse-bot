import youtube_uploader
import sys
import os

def test_yt_upload():
    video_path = "reels_output/test_reel.mp4"
    if not os.path.exists(video_path):
        print(f"Hata: {video_path} bulunamadı!")
        sys.exit(1)

    print(f"Test videosu '{video_path}' YouTube Shorts'a yükleniyor...")
    
    title = "Test Video 🖤"
    description = "Bu bir otomatik test videosudur. Deathlipse.\n\n#shorts"
    tags = ["test", "goth", "metal", "streetwear"]
    
    success = youtube_uploader.upload_video_to_shorts(video_path, title, description, tags)
    
    if success:
        print("\n✅ TEBRİKLER! YouTube yüklemesi BAŞARILI.")
        print("token.json dosyası başarıyla oluşturuldu ve yetkilendirme çalışıyor.")
    else:
        print("\n❌ YouTube yüklemesi BAŞARISIZ oldu.")

if __name__ == "__main__":
    test_yt_upload()
