import os
import subprocess

songs = {
    "dark_ambient": [
        "Gathering Darkness Kevin MacLeod",
        "The End Karl Casey White Bat Audio",
        "Chasm Alexander Nakarada",
        "Hush Kevin MacLeod",
        "Forsaken Alexander Nakarada",
        "Night Rider Karl Casey",
        "Shadowlands 5 Antechamber Kevin MacLeod"
    ],
    "mid_tempo": [
        "Wrath Alexander Nakarada",
        "Industrial Cinematic Kevin MacLeod",
        "Blood Eagle Alexander Nakarada",
        "Metalmania Kevin MacLeod",
        "Clash of Gods Alexander Nakarada",
        "Decisions Kevin MacLeod"
    ],
    "heavy": [
        "Hell Alexander Nakarada",
        "Killers Kevin MacLeod",
        "Unstoppable Alexander Nakarada",
        "Mjolnir Alexander Nakarada",
        "Curse of the Scarab Kevin MacLeod",
        "Viking Metal Alexander Nakarada"
    ]
}

def download_song(category, query):
    os.makedirs(f"assets/audio/{category}", exist_ok=True)
    out_tmpl = f"assets/audio/{category}/%(title)s.%(ext)s"
    cmd = [
        "yt-dlp",
        f"ytsearch1:{query}",
        "--extract-audio",
        "--audio-format", "mp3",
        "--audio-quality", "0",
        "-o", out_tmpl,
        "--match-filter", "duration < 600",
        "--no-playlist"
    ]
    print(f"Downloading {query} to {category}...")
    subprocess.run(cmd)

if __name__ == "__main__":
    for cat, qs in songs.items():
        for q in qs:
            download_song(cat, q)
    print("ALL SONGS DOWNLOADED!")
