from discord import VoiceClient, VoiceChannel
import discord


class MusicSource:
    def __init__(self, url, name) -> None:
        self.url = url
        self.name = name
