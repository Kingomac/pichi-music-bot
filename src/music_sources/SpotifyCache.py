from discord import Message, VoiceClient, FFmpegOpusAudio
import subprocess
import json
import os
import random
import asyncio
from queue import Queue
import yt_dlp


class SpotifyCache:
    def __init__(self, url: str, name: str) -> None:
        self.url = url
        self.name = name
        self.song_queue = None
        self.voice_client = None
        self.channel_asked = None

    @staticmethod
    def create_list() -> None:
        file = open("cached/list.json", "w+")
        file.write(json.dumps({}))
        file.close()

    def add_to_list(self) -> None:
        if not os.path.exists("cached/list.json"):
            SpotifyCache.create_list()
        file = open("cached/list.json", "r")
        data = json.load(file)
        file.close()
        data[self.name] = self.url
        file = open("cached/list.json", "w")
        file.write(json.dumps(data))
        file.close()

    @staticmethod
    async def read_list(message: Message):
        if not os.path.exists("cached/list.json"):
            await message.reply("no existe lista 😫😫 voy a crearla")
            SpotifyCache.create_list()
        file = open("cached/list.json", "r")
        data: dict = json.load(file)
        file.close()
        toret = ""
        for key in data:
            print(key, "->", data[key])
            toret += f"{key}: {data[key]}\n"
        await message.reply(toret)

    async def download(self, message: Message) -> None:
        await message.reply("a sus ordenes mi capitan")
        if os.path.exists("cached"):
            os.mkdir("cached")
        if os.path.exists(f"cached/{self.name}"):
            raise Exception()
        os.mkdir(f"cached/{self.name}")
        result = -1
        if "spotify" in self.url:
            result = self.download_spotify()
        elif "yout" in self.url:
            result = self.download_youtube()
        else:
            message.reply(
                "pero que usas bro, pasa una playlist de spotify o youtube, rarete no?"
            )
            return
        if result == 0:
            self.add_to_list()
            await message.channel.send(
                f"listo gfe <@{message.author.id}>, ya puedes escuchar tus rulas"
            )
        else:
            await message.channel.send(f"turboliada con código {result.returncode}")

    def download_youtube(self):
        with yt_dlp.YoutubeDL(
            {
                "format": "opus/bestaudio/best",
                "outtmpl": f"cached/{self.name}/%(title)s.%(ext)s",
                "postprocessors": [
                    {  # Extract audio using ffmpeg
                        "key": "FFmpegExtractAudio",
                        "preferredcodec": "opus",
                    }
                ],
            }
        ) as ydl:
            ydl.download([self.url])
        return 0

    def download_spotify(self):
        result = subprocess.run(
            [
                "python",
                "-m",
                "spotdl",
                "--format",
                "opus",
                "--output",
                f"cached/{self.name}",
                "sync",
                self.url,
                "--save-file",
                f"cached/{self.name}/syncfile.sync.spotdl",
            ],
            capture_output=True,
        )
        print(
            f"download ended with code {result.returncode} and stdout: {result.stdout} and stderr: {result.stderr}"
        )
        if result.returncode == 0:
            return 0
        return result.returncode

    async def play_playlist(self, voice_client: VoiceClient, message: Message) -> None:
        if not os.path.exists(f"cached/{self.name}"):
            await message.reply("no existe 😿😿")
            return
        song_list = list(
            filter(
                lambda entry: (entry.endswith(".opus")),
                os.listdir(f"cached/{self.name}"),
            )
        )
        self.song_queue = Queue(len(song_list))
        while len(song_list) > 0:
            self.song_queue.put(song_list.pop(random.randint(0, len(song_list) - 1)))
        print(f"song queue created: {self.song_queue}")
        self.voice_client = voice_client
        self.channel_asked = message.channel
        voice_client.play(
            FFmpegOpusAudio(f"cached/{self.name}/{self.song_queue.get()}"),
            after=self.after_song,
        )

    def after_song(self, err: Exception):
        if err != None:
            print("after-song error: " + err)
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run_coroutine_threadsafe(self.after_song_fail(), loop=loop)
            return
        if self.song_queue.empty():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run_coroutine_threadsafe(self.after_song_empty(), loop=loop)
            return
        next_song = self.song_queue.get()
        print(f"next song: {next_song}")
        self.voice_client.play(
            FFmpegOpusAudio(f"cached/{self.name}/{next_song}"), after=self.after_song
        )

    async def after_song_fail(self):
        await self.channel_asked.send(f"que problemas")

    async def after_song_empty(self):
        await self.voice_client.disconnect()
        await self.channel_asked.send(
            "se acabó la música, poned esta ahora: https://youtu.be/dQw4w9WgXcQ"
        )
