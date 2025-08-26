from ai_clips_maker import Transcriber, ClipFinder, resize

# Step 1: Transcription
transcriber = Transcriber()
transcription = transcriber.transcribe(audio_path="/home/michael_adegoke/testvideo.webm", lang= "en")

# Step 2: Clip detection
clip_finder = ClipFinder()
clips = clip_finder.find_clips(transcription=transcription)
print(clips[0].start_time, clips[0].end_time)

# Step 3: Cropping & resizing
crops = resize(
    video_file_path="/home/michael_adegoke/testvideo.webm",
    #pyannote_auth_token="your_huggingface_token",
    aspect_ratio=(9, 16)
)
print(crops.segments)