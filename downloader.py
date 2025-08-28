from pytube import YouTube

url = "https://www.youtube.com/watch?v=luVgetzI97Q"  # replace with your link
output_path = "/home/michael_adegoke"  # where you want the file saved
filename = "testvideo.mp4"

yt = YouTube(url)
stream = yt.streams.filter(progressive=True, file_extension="mp4")\
                   .order_by("resolution")\
                   .desc()\
                   .first()

print(f"Downloading: {yt.title} at {stream.resolution}")
stream.download(output_path=output_path, filename=filename)
print(f"✅ Download complete: {output_path}/{filename}")
