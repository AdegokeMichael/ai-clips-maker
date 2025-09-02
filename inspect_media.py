from ai_clips_maker.media.temporal_media_file import TemporalMediaFile


def inspect_media(path: str):
    media = TemporalMediaFile(path)
    print("\n=== Media Inspection ===")
    print(f"Path: {path}")
    print(f"Type: {media.get_type()}")
    print(f"Duration (s): {media.get_duration()}")
    print(f"Audio bitrate: {media.get_bitrate('a:0')}")
    print(f"Video bitrate: {media.get_bitrate('v:0')}")


if __name__ == "__main__":
    inspect_media("downloads/Free_software__free_society__Richard_Stallman_at_TEDxGeneva_2014.mp4")