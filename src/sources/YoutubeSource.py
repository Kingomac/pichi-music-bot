from sources.MusicSource import MusicSource
from discord import VoiceClient, FFmpegPCMAudio
import yt_dlp


class YoutubeSource(MusicSource):
    def __init__(self, url, name) -> None:
        super().__init__(url, name)

    def play_in(self, voice_client: VoiceClient):
        print(f"Playing Youtube audio from: " + self.url)
        with yt_dlp.YoutubeDL({
            'format': 'opus/bestaudio/best',
            'postprocessors': [{  # Extract audio using ffmpeg
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'm4a',
            }]
        }) as ydl:
            info: dict = ydl.sanitize_info(
                ydl.extract_info(self.url, download=False))
            voice_client.play(FFmpegPCMAudio(
                info['url']))
