from sources.MusicSource import MusicSource
from discord import Message, VoiceClient, FFmpegOpusAudio
import subprocess
import json
import os
import random
import asyncio
import threading
from queue import Queue


class SpotifyCache(MusicSource):
    def __init__(self, url: str, name: str) -> None:
        super().__init__(url, name)
        self.song_queue = None
        self.voice_client = None
        self.channel_asked = None

    def create_list() -> None:
        file = open('cached/list.json', 'w')
        file.write(json.dumps({}))
        file.close()

    def add_to_list(self) -> None:
        file = open('cached/list.json', 'r')
        data = json.load(file.read())
        file.close()
        data[self.name] = self.url
        file = open('cached/list.json', 'w')
        file.write(json.dumps(data))
        file.close()

    async def read_list(message: Message):
        file = open('cached/list.json', 'r')
        data: dict = json.load(file.read())
        file.close()
        toret = ""
        for key in data:
            print(key, "->", data[key])
            toret += f'{key}: {data[key]}\n'
        await message.reply(toret)

    async def download(self, message: Message) -> None:
        await message.reply("a sus ordenes mi capitan")
        result = subprocess.run(["python", "-m", "spotdl", "--format",
                                 "opus", "--output", f"cached/{self.name}", "sync", self.url, "--save-file", f"cached/{self.name}/syncfile.sync.spotdl"], capture_output=True)
        print(
            f"download ended with code {result.returncode} and stdout: {result.stdout} and stderr: {result.stderr}")
        if result.returncode == 0:
            await message.channel.send(f"listo gfe <@{message.author.id}>, ya puedes escuchar tus rulas")
        else:
            await message.channel.send(f"turboliada con código {result.returncode}, stdout -> {result.stdout} y stderr -> {result.stderr}")

    async def play_playlist(self, voice_client: VoiceClient, message: Message) -> None:
        if not os.path.exists(f'cached/{self.name}'):
            await message.reply("no existe 😿😿")
            return
        song_list = list(filter(lambda entry: (entry.endswith(
            ".opus")), os.listdir(f'cached/{self.name}')))
        self.song_queue = Queue(len(song_list))
        while (len(song_list) > 0):
            self.song_queue.put(song_list.pop(
                random.randint(0, len(song_list)-1)))
        print(f"song queue created: {self.song_queue}")
        self.voice_client = voice_client
        self.channel_asked = message.channel
        voice_client.play(FFmpegOpusAudio(
            f'cached/{self.name}/{self.song_queue.get()}'), after=self.after_song)

    def after_song(self, err: Exception):
        if err != None:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run_coroutine_threadsafe(
                self.after_song_fail, loop=loop)
        if self.song_queue.empty():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            asyncio.run_coroutine_threadsafe(
                self.after_song_empty, loop=loop)
            return
        self.voice_client.play(FFmpegOpusAudio(
            self.song_queue.get()), after=self.after_song)

    async def after_song_fail(self):
        await self.channel_asked.send(f"que problemas")

    async def after_song_empty(self):
        await self.voice_client.disconnect()
        await self.channel_asked.send("se acabó la música, poned esta ahora: https://youtu.be/dQw4w9WgXcQ")
