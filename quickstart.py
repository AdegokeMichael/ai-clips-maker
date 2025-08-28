from ai_clips_maker import Transcriber, ClipFinder, resize
from pytube import YouTube
from dotenv import load_dotenv
import subprocess
import os
import re

# --- Load .env variables ---
load_dotenv()
url = os.getenv("YOUTUBE_URL")

# --- Step 0: Download video with safe title ---
output_path = "/home/michael_adegoke"

yt = YouTube(url)
# Clean up title to make it filename-safe
safe_title = re.sub(r'[^a-zA-Z0-9_\- ]', '', yt.title).replace(" ", "_")
filename = f"{safe_title}.mp4"
download_path = os.path.join(output_path, filename)

if not os.path.exists(download_path):
    print(f"📥 Downloading: {yt.title}")
    stream = yt.streams.filter(progressive=True, file_extension="mp4")\
                       .order_by("resolution")\
                       .desc()\
                       .first()
    stream.download(output_path=output_path, filename=filename)
    print(f"✅ Download complete: {download_path}")
else:
    print(f"⚡ Already downloaded: {download_path}")

# --- Step 1: Transcription ---
transcriber = Transcriber()
transcription = transcriber.transcribe(audio_path=download_path, lang="en")

# --- Step 2: Clip detection ---
clip_finder = ClipFinder()
clips = clip_finder.find_clips(transcription=transcription)

print(f"🎬 Found {len(clips)} clips")
if len(clips) > 0:
    print("First clip timestamps:", clips[0].start_time, clips[0].end_time)

# --- Step 3: Cropping & resizing (optional, for shorts format) ---
crops = resize(
    video_file_path=download_path,
    aspect_ratio=(9, 16)
)
print("Detected segments:", crops.segments)

# --- Step 4: Save clips with ffmpeg ---
clips_output_dir = os.path.join(output_path, f"{safe_title}_clips")
os.makedirs(clips_output_dir, exist_ok=True)

for i, clip in enumerate(clips, start=1):
    start_time = clip.start_time
    end_time = clip.end_time
    duration = end_time - start_time

    output_file = os.path.join(clips_output_dir, f"{safe_title}_clip{i}.mp4")

    # ffmpeg command to cut clip
    command = [
        "ffmpeg", "-y",
        "-i", download_path,
        "-ss", str(start_time),
        "-t", str(duration),
        "-c", "copy",
        output_file
    ]

    print(f"✂️ Exporting {output_file}...")
    subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    print(f"✅ Saved {output_file}")







"""

from ai_clips_maker import Transcriber, ClipFinder, resize
from pytube import YouTube
from dotenv import load_dotenv
import os

# --- Load .env variables ---
load_dotenv()
url = os.getenv("YOUTUBE_URL")

# --- Step 0: Download video if not exists ---
output_path = "/home/michael_adegoke"
filename = "testvideo.mp4"
download_path = os.path.join(output_path, filename)

if not os.path.exists(download_path):
    print("📥 Downloading video...")
    yt = YouTube(url)
    stream = yt.streams.filter(progressive=True, file_extension="mp4")\
                       .order_by("resolution")\
                       .desc()\
                       .first()
    stream.download(output_path=output_path, filename=filename)
    print(f"✅ Download complete: {download_path}")
else:
    print(f"⚡ Video already exists: {download_path}")

# --- Step 1: Transcription ---
transcriber = Transcriber()
transcription = transcriber.transcribe(audio_path=download_path, lang="en")

# --- Step 2: Clip detection ---
clip_finder = ClipFinder()
clips = clip_finder.find_clips(transcription=transcription)
print(clips[0].start_time, clips[0].end_time)

# --- Step 3: Cropping & resizing ---
crops = resize(
    video_file_path=download_path,
    #pyannote_auth_token="your_huggingface_token",
    aspect_ratio=(9, 16)
)
print(crops.segments)

"""