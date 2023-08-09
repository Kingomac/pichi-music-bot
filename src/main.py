import os
import discord
from dotenv import load_dotenv
from sources.YoutubeSource import YoutubeSource as YTSource
from sources.MusicSource import MusicSource
from sources.SpotifyCache import SpotifyCache

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILDS = os.getenv("DISCORD_GUILDS").strip("[]").split(", ")
CALL_NAME = "pichi" + " "
print(DISCORD_GUILDS)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
voice_client: discord.VoiceClient | None = None


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name in DISCORD_GUILDS:
            print(f'{client.user} está conectado en: {guild.name}')
        else:
            print(f'{client.user} está conectado en: {guild.name}, que no está en la lista de servidores admitidos, entonces lo abandona')
            guild.leave()


@client.event
async def on_message(message: discord.Message):
    global voice_client
    texto: str = message.content
    print(texto)
    channel = message.author.voice.channel
    if not texto.startswith(CALL_NAME) or message.author.name == CALL_NAME:
        return
    comando = texto[len(CALL_NAME):]
    print(f"comando: {comando}")

    if comando.startswith("canta lista "):
        name_list = comando[len("canta lista "):]
        print(f"gonna play list {name_list}")
        source = SpotifyCache(url="", name=name_list)
        voice_client = await source.connect_to_voice_channel(voice_client=voice_client, voice_channel=channel)
        await source.play_playlist(voice_client=voice_client, message=message)
    elif comando.startswith("canta "):
        link = comando[len("canta "):]
        source: MusicSource = None
        if "https://youtu" in link:
            source = YTSource(url=link, name="")
            voice_client = await source.connect_to_voice_channel(
                voice_client=voice_client, voice_channel=channel)
            source.play_in(voice_client=voice_client)
        else:
            print("Unexpected link")
            await message.reply(
                "que coño acabas de mandar bro, vete a dar un paseo 🚶‍♂️🚶‍♂️🚶‍♂️")
    elif comando.startswith("descarga "):
        params = comando[len("descarga "):]
        params = params.split(" ")
        name = params[0]
        url = params[1]
        print(f"url: {url}, name: {name}, params: {params}")
        if not "https://open.spotify" in url:
            print("invalid url to download")
            await message.reply("url pocha")
            raise Exception("bad url")
        if "teemo" in name.lower():
            await message.reply("no tienes alma, diablo")
            raise Exception("dirty mind")
        source = SpotifyCache(url, name)
        await source.download(message=message)


@client.event
async def on_voice_state_update(member, before, after):
    global voice_client
    voice_state = member.guild.voice_client
    if voice_state is not None and len(voice_state.channel.members) == 1:
        voice_state.stop()
        await voice_state.disconnect()

client.run(DISCORD_TOKEN)
