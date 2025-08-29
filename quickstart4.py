import os
import re
import subprocess
from dotenv import load_dotenv

# Import ai-clips-maker modules
from ai_clips_maker import Transcriber, ClipFinder, resize
from ai_clips_maker.txtslice.matcher import MediaSegment  # so we can handle clip objects

# Load environment variables
load_dotenv()

url = os.getenv("YOUTUBE_URL")
download_path = os.getenv("DOWNLOAD_PATH", "downloads")
use_auto_split = os.getenv("USE_AUTO_SPLIT", "True").lower() == "true"

# Ensure download folder exists
os.makedirs(download_path, exist_ok=True)

def sanitize_filename(name: str, max_length: int = 150) -> str:
    """Sanitize filenames by replacing unsafe chars and limiting length."""
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', name)
    return safe[:max_length]

# Step 1: Download video
print("⬇️ Downloading video with yt-dlp...")
subprocess.run([
    "yt-dlp",
    "-f", "bv*[ext=mp4]+ba[ext=m4a]/b[ext=mp4]",
    "-o", os.path.join(download_path, "%(title)s.%(ext)s"),
    "--write-info-json",
    "--write-subs",
    "--write-auto-subs",
    "--cookies", os.path.join(os.getcwd(), "cookies.txt"),
    url
], check=True)

# Step 1b: Find and sanitize all downloaded files (video + sidecars)
all_files = os.listdir(download_path)
video_files = [f for f in all_files if f.endswith(".mp4")]
if not video_files:
    raise FileNotFoundError("❌ Video file not found after download")

# The raw base filename before sanitization
raw_video_file = os.path.join(download_path, video_files[0])
raw_base, raw_ext = os.path.splitext(os.path.basename(raw_video_file))
safe_base = sanitize_filename(raw_base)
video_file = os.path.join(download_path, safe_base + raw_ext)

# Rename main video if needed
if raw_video_file != video_file:
    os.rename(raw_video_file, video_file)
    print(f"🧹 Renamed video → {video_file}")

# Rename all sidecar files (.json, .vtt, .srt, etc.) to match sanitized base
for f in all_files:
    if f.startswith(raw_base) and f != os.path.basename(raw_video_file):
        raw_path = os.path.join(download_path, f)
        new_name = f.replace(raw_base, safe_base, 1)
        new_path = os.path.join(download_path, sanitize_filename(new_name))
        os.rename(raw_path, new_path)
        print(f"🧹 Renamed sidecar → {new_path}")

print(f"✅ Download complete: {video_file}")

# Step 2: Generate clips
clips: list[MediaSegment] = []

if use_auto_split:
    print("📝 Transcribing + AI highlight detection...")
    transcriber = Transcriber()
    transcription = transcriber.transcribe(video_file)

    clip_finder = ClipFinder()
    clips = clip_finder.find_clips(transcription=transcription)

    if not clips:
        print("⚠️ No clips detected, falling back to full video.")
        clips = [MediaSegment(start_time=0, end_time=None)]
else:
    print("⏱ Using fixed time-based splitting...")
    import cv2
    cap = cv2.VideoCapture(video_file)
    total_duration = int(cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS))
    cap.release()

    clip_length = 60  # seconds
    clips = [
        MediaSegment(start_time=i, end_time=min(i + clip_length, total_duration))
        for i in range(0, total_duration, clip_length)
    ]

# Step 3: Export clips
for idx, clip in enumerate(clips):
    start = clip.start_time
    end = clip.end_time

    raw_clip_name = f"{safe_base}_clip_{idx+1}.mp4"
    safe_clip_name = sanitize_filename(raw_clip_name)
    clip_path = os.path.join(download_path, safe_clip_name)

    cmd = [
        "ffmpeg", "-i", video_file,
        "-ss", str(start),
        "-to", str(end) if end else "",
        "-c", "copy", clip_path
    ]
    cmd = [c for c in cmd if c]  # remove empty args
    subprocess.run(cmd, check=True)
    print(f"🎬 Clip saved: {clip_path}")

    # Step 4: Resize/crop
    print("📱 Resizing for TikTok/IG...")
    crops = resize(
        video_file_path=clip_path,
        pyannote_auth_token=os.getenv("PYANNOTE_AUTH_TOKEN"),  # required arg
        aspect_ratio=(9, 16)
    )
    print(f"✅ Cropped segments for {clip_path}: {crops.segments}")
