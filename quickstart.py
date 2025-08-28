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
from ai_clips_maker import Transcriber, ClipFinder, resize

# Step 1: Transcription
transcriber = Transcriber()
transcription = transcriber.transcribe(audio_path="/home/michael_adegoke/testvideo.mp4", lang= "en")

# Step 2: Clip detection
clip_finder = ClipFinder()
clips = clip_finder.find_clips(transcription=transcription)
print(clips[0].start_time, clips[0].end_time)

# Step 3: Cropping & resizing
crops = resize(
    video_file_path="/home/michael_adegoke/testvideo.mp4",
    #pyannote_auth_token="your_huggingface_token",
    aspect_ratio=(9, 16)
)
print(crops.segments)
"""