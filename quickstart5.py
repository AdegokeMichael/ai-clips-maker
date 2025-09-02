import os
import re
import subprocess
from dotenv import load_dotenv
from pathlib import Path

# Import ai-clips-maker modules
from ai_clips_maker import Transcriber, ClipFinder, resize
# from ai_clips_maker.txtslice.matcher import MediaSegment  # handle clip objects
# wrong
# from ai_clips_maker.txtslice.matcher import MediaSegment

# correct
# from ai_clips_maker.media.temporal_media_file import TemporalMediaFile
from ai_clips_maker.media.temporal_media_file import TemporalMediaFile as MediaSegment




# Load environment variables
load_dotenv()

url = os.getenv("YOUTUBE_URL")
download_path = Path(os.getenv("DOWNLOAD_PATH", "downloads"))
use_auto_split = os.getenv("USE_AUTO_SPLIT", "True").lower() == "true"

# Ensure download folder exists
download_path.mkdir(parents=True, exist_ok=True)

def sanitize_filename(name: str, max_length: int = 150) -> str:
    """Sanitize filenames by replacing unsafe chars and limiting length."""
    safe = re.sub(r'[^A-Za-z0-9._-]', '_', name)
    return safe[:max_length].strip("._")  # avoid trailing dots/underscores

# Step 1: Download video
print("⬇️ Downloading video with yt-dlp...")
subprocess.run([
    "yt-dlp",
    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]",
    "-o", str(download_path / "%(title)s.%(ext)s"),
    "--merge-output-format", "mp4",  # force a clean .mp4 container
    "--write-info-json",
    "--write-subs",
    "--write-auto-subs",
    "--cookies", str(Path.cwd() / "cookies.txt"),
    url
], check=True)

# Step 1b: Find the most recent .mp4 file
video_files = list(download_path.glob("*.mp4"))
if not video_files:
    raise FileNotFoundError("❌ No .mp4 video file found after download")

latest_video = max(video_files, key=lambda f: f.stat().st_mtime)
raw_base, raw_ext = os.path.splitext(latest_video.name)
safe_base = sanitize_filename(raw_base)
video_file = download_path / (safe_base + raw_ext)

# Rename video if needed
if latest_video != video_file:
    latest_video.rename(video_file)
    print(f"🧹 Renamed video → {video_file}")

# Rename sidecar files to match sanitized base
for f in download_path.iterdir():
    if f.name.startswith(raw_base) and f != latest_video:
        new_name = f.name.replace(raw_base, safe_base, 1)
        f.rename(download_path / sanitize_filename(new_name))
        print(f"🧹 Renamed sidecar → {download_path / sanitize_filename(new_name)}")

print(f"✅ Download complete: {video_file}")

# Step 2: Generate clips
clips: list[MediaSegment] = []

if use_auto_split:
    print("📝 Transcribing + AI highlight detection...")
    transcriber = Transcriber()
    transcription = transcriber.transcribe(str(video_file))

    clip_finder = ClipFinder()
    clips = clip_finder.find_clips(transcription=transcription)

    if not clips:
        print("⚠️ No clips detected, falling back to full video.")
        clips = [MediaSegment(start_time=0, end_time=None)]
else:
    print("⏱ Using fixed time-based splitting...")
    import cv2
    cap = cv2.VideoCapture(str(video_file))
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
    clip_path = download_path / safe_clip_name

    cmd = [
        "ffmpeg", "-i", str(video_file),
        "-ss", str(start),
        "-to", str(end) if end else "",
        "-c", "copy", str(clip_path)
    ]
    cmd = [c for c in cmd if c]  # remove empty args
    subprocess.run(cmd, check=True)
    print(f"🎬 Clip saved: {clip_path}")

    # Step 4: Resize/crop
    print("📱 Resizing for TikTok/IG...")
    crops = resize(
        video_file_path=str(clip_path),
        pyannote_auth_token=os.getenv("PYANNOTE_AUTH_TOKEN"),  # required arg
        aspect_ratio=(9, 16)
    )
    print(f"✅ Cropped segments for {clip_path}: {crops.segments}")
