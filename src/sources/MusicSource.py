from discord import VoiceClient, VoiceChannel
import discord


class MusicSource:
    def __init__(self, url, name) -> None:
        self.url = url
        self.name = name

    async def connect_to_voice_channel(
        self, voice_client: VoiceClient, voice_channel: VoiceChannel
    ):
        if (
            voice_client != None
            and voice_client.is_connected()
            and discord.VoiceClient.channel != voice_channel
        ):
            voice_client.disconnect()
        if voice_client == None or not voice_client.is_connected():
            voice_client = await discord.VoiceChannel.connect(voice_channel)
        return voice_client
