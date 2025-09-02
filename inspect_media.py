from ai_clips_maker.filesys import object as obj

def inspect_media(path: str):
    media = obj.TemporalMediaFile(path)
    print("\n=== Media Inspection ===")
    print(f"Path: {path}")
    print(f"Duration (s): {media.duration}")
    print(f"Has video: {media.has_video}")
    print(f"Has audio: {media.has_audio}")
    print(f"Video streams: {media.video_streams}")
    print(f"Audio streams: {media.audio_streams}")
    print("========================\n")

if __name__ == "__main__":
    inspect_media("downloads/Free_software__free_society__Richard_Stallman_at_TEDxGeneva_2014.mp4")
