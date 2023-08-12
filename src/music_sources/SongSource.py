import subprocess
import yt_dlp
import random
from queue import Queue


class SongSource:
    def get_audio_url(link: str):
        if link.startswith("https://open.spotify.com/track"):
            proc = subprocess.run(
                ["python", "-m", "spotdl", "url", link], capture_output=True
            )
            return str(proc.stdout).split("\\n")[2].removesuffix("\\r")
        elif link.startswith("https://youtu"):
            with yt_dlp.YoutubeDL(
                {
                    "format": "opus/bestaudio/best",
                    "postprocessors": [
                        {  # Extract audio using ffmpeg
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "opus",
                        }
                    ],
                }
            ) as ydl:
                info: dict = ydl.sanitize_info(ydl.extract_info(link, download=False))
                return info["url"]

    def get_list_urls(link: str, result_queue: Queue):
        if "youtu" in link and "list=" in link:
            with yt_dlp.YoutubeDL(
                {
                    "format": "opus/bestaudio/best",
                    "postprocessors": [
                        {  # Extract audio using ffmpeg
                            "key": "FFmpegExtractAudio",
                            "preferredcodec": "opus",
                        }
                    ],
                }
            ) as ydl:
                info = ydl.sanitize_info(ydl.extract_info(link, download=False))
                urls = list(map(lambda x: x["url"], info["entries"]))
                while len(urls) > 0:
                    result_queue.put(urls.pop(random.randint(0, len(urls) - 1)))
        elif "spotify" in link and "playlist" in link:
            print("link lista spotify a descargar: " + link)
            proc = subprocess.run(
                ["python", "-m", "spotdl", "--format", "opus", "url", link],
                capture_output=True,
            )
            if proc.returncode != 0:
                print("error: " + proc.stderr)
                return
            output = str(proc.stdout).split("\\n")
            output = output[3 : len(output) - 2]
            output = list(
                map(
                    lambda x: x.strip().removesuffix("\\r"),
                    filter(
                        lambda x: "https://" in x and "spotify.com" not in x,
                        output,
                    ),
                )
            )

            while len(output) > 0:
                result_queue.put(output.pop(random.randint(0, len(output) - 1)))
