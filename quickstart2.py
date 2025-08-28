import os
import json
import subprocess
from dotenv import load_dotenv

# --- Load .env variables ---
load_dotenv()
url = os.getenv("YOUTUBE_URL")
download_path = os.getenv("DOWNLOAD_PATH")
clips_output_base = os.getenv("CLIPS_PATH")
auto_split = os.getenv("AUTO_SPLIT", "True").lower() == "true"
clip_min = int(os.getenv("CLIP_MIN", 30))
clip_max = int(os.getenv("CLIP_MAX", 60))

os.makedirs(download_path, exist_ok=True)
os.makedirs(clips_output_base, exist_ok=True)

if not url:
    raise ValueError("❌ Missing YOUTUBE_URL in .env")

# --- Download video + metadata using yt-dlp ---
print("⬇️ Downloading video with yt-dlp...")

video_template = os.path.join(download_path, "%(title)s.%(ext)s")

subprocess.run([
    "yt-dlp",
    "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
    "-o", os.path.join(download_path, "%(title)s.%(ext)s"),
    "--write-info-json",
    "--cookies-from-browser", "firefox",  # change to "chrome" if you use Chrome
    url
], check=True)
print("✅ Download complete.")

# --- Find metadata JSON file ---
json_files = [f for f in os.listdir(download_path) if f.endswith(".info.json")]
if not json_files:
    raise FileNotFoundError("❌ Could not find yt-dlp metadata JSON")

with open(os.path.join(download_path, json_files[0]), "r", encoding="utf-8") as f:
    metadata = json.load(f)

# --- Extract info from metadata ---
video_title = metadata.get("title", "untitled").replace(" ", "_")
video_duration = metadata.get("duration", 0)  # in seconds
video_filename = metadata.get("_filename")   # full path of downloaded file

if not video_filename or not os.path.exists(video_filename):
    raise FileNotFoundError("❌ Video file not found after download")

print(f"📹 Title: {video_title}")
print(f"⏱️ Duration: {video_duration}s")
print(f"📂 Saved to: {video_filename}")

# --- Create clips output directory ---
clips_output_dir = os.path.join(clips_output_base, video_title)
os.makedirs(clips_output_dir, exist_ok=True)

# --- Define clip class ---
class Clip:
    def __init__(self, start, end):
        self.start_time = start
        self.end_time = end

# --- Placeholder for detection logic ---
clips = []  # AI-detected timestamps would go here

# --- If no clips detected, maybe auto-split ---
if not clips:
    if auto_split:
        print("⚠️ No AI-detected clips. Falling back to auto-split mode...")
        clips = []
        start = 0
        while start < video_duration:
            end = min(start + clip_max, video_duration)
            clips.append(Clip(start, end))
            start += clip_max
    else:
        print("⚠️ No AI-detected clips and AUTO_SPLIT=False. Exiting.")
        exit(0)

# --- Export clips ---
for i, clip in enumerate(clips, start=1):
    start_time = clip.start_time
    end_time = clip.end_time
    duration = end_time - start_time

    if duration < clip_min:
        print(f"⏭️ Skipping clip{i} ({duration:.1f}s) – shorter than CLIP_MIN")
        continue
    elif duration > clip_max:
        print(f"⚖️ Trimming clip{i} ({duration:.1f}s) to CLIP_MAX={clip_max}")
        duration = clip_max

    output_file = os.path.join(clips_output_dir, f"{video_title}_clip{i}.mp4")

    command = [
        "ffmpeg", "-y",
        "-i", video_filename,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c", "copy",
        output_file
    ]

    print(f"✂️ Exporting {output_file}...")
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ Saved {output_file}")
print("🎉 All done!")