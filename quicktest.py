
import os
from ai_clips_maker.media.temporal_media_file import TemporalMediaFile

def process_media(path: str):
    # Create TemporalMediaFile object
    media = TemporalMediaFile(path)

    # Check validity
    msg = media.check_exists()
    if msg is not None:
        print(f"[Error] {msg}")
        return

    # Print info
    print(f"=== Processing {path} ===")
    print(f"Type: {media.get_type()}")
    print(f"Duration (s): {media.get_duration()}")
    print(f"Audio bitrate: {media.get_bitrate('a:0')}")
    print(f"Video bitrate: {media.get_bitrate('v:0')}")

    # 🎯 Here you can hook in your clip-detection logic
    # For example, later you'll analyze frames with CLIP or whatever detection logic you add.
    # But for now, let’s just confirm metadata works fine.


if __name__ == "__main__":
    test_file = "downloads/Free_software__free_society__Richard_Stallman_at_TEDxGeneva_2014.mp4"
    
    if not os.path.exists(test_file):
        print(f"[Error] File not found: {test_file}")
    else:
        process_media(test_file)
