from discord import VoiceClient, VoiceChannel, FFmpegOpusAudio
from queue import Queue
import asyncio


class MusicController:
    def __init__(self) -> None:
        self.song_queue = Queue()
        self.voice_client = None
        self.voice_channel = None

    def put(self, item: str):
        self.song_queue.put(item)

    async def connect_to_voice_channel(self, voice_channel: VoiceChannel):
        if (
            self.voice_client != None
            and self.voice_client.is_connected()
            and self.voice_client.channel != voice_channel
        ):
            self.voice_client.disconnect()
        if self.voice_client == None or not self.voice_client.is_connected():
            self.voice_client = await VoiceChannel.connect(voice_channel)
        self.voice_channel = voice_channel

    def stop(self):
        self.voice_client.stop()

    def play(self, *ctx):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        if self.song_queue.empty():
            print("empty queue")
            return

        song = self.song_queue.get()
        source = FFmpegOpusAudio(
            song,
            before_options="-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5",
            options='-vn -filter:a "volume=0.25"',
        )
        self.voice_client.play(source=source, after=self.play)

    def is_playing(self):
        return self.voice_client.is_playing()

    def pause(self):
        self.voice_client.pause()

    def resume(self):
        self.voice_client.resume()
