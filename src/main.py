import os
import discord
from dotenv import load_dotenv
from music_sources.SpotifyCache import SpotifyCache
from controllers.MusicController import MusicController
from music_sources.SongSource import SongSource

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILDS = os.getenv("DISCORD_GUILDS").strip("[]").split(", ")
CALL_NAME = "pichi" + " "
print(DISCORD_GUILDS)
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
music_controller = MusicController()


@client.event
async def on_ready():
    for guild in client.guilds:
        if guild.name in DISCORD_GUILDS:
            print(f"{client.user} está conectado en: {guild.name}")
        else:
            print(
                f"{client.user} está conectado en: {guild.name}, que no está en la lista de servidores admitidos, entonces lo abandona"
            )
            guild.leave()


@client.event
async def on_message(message: discord.Message):
    global voice_client
    texto: str = message.content
    print(texto)
    if not texto.startswith(CALL_NAME) or message.author.name == CALL_NAME:
        return
    comando = texto[len(CALL_NAME) :]
    print(f"comando: {comando}")

    if comando.startswith("canta "):
        if message.author.voice.channel is None:
            await message.reply("y donde canto, debajo del mar?? 😩😩")
            return

        await music_controller.connect_to_voice_channel(
            voice_channel=message.author.voice.channel
        )
        music_source = comando[len("canta ") :]

        if music_source.startswith("lista "):
            list_data = music_source[len("lista ") :]
            if list_data.startswith("https://"):
                print("https list, let's play")
                SongSource.get_list_urls(
                    link=list_data, result_queue=music_controller.song_queue
                )
                if not music_controller.is_playing():
                    music_controller.play()
            else:
                list_data = list_data.split(" ")
                print(f"list_data = {list_data}")
                if (
                    not list_data[1].strip().startswith("https://")
                    or "list" not in list_data[1]
                ):
                    await message.reply("y la playlist???")
                    return
                else:
                    list_name = list_data[0]
                    list_url = list_data[1]
                    print(f"list_name = {list_name} ; list_url: {list_url}")
                    source = SpotifyCache(url=list_url, name=list_name)
                    await source.download(message=message)

            ## TODO -> comprobar si la lista está descargada, en caso de que no lo esté reproducirla por stream
        else:
            if "list" in music_source and "youtu" in music_source:
                music_source = music_source.split("?list")[0]
            elif "list" in music_source:
                await message.reply(f"no me metas playlists guarrindongo")
                return
            try:
                music_controller.add_to_queue(
                    SongSource.get_audio_url(link=music_source)
                )
                if not music_controller.is_playing():
                    music_controller.play()
            except Exception as err:
                await message.reply(f"que problemas: {err[:1500]}")


"""""

    if comando.startswith("canta lista "):
        name_list = comando[len("canta lista ") :]
        print(f"gonna play list {name_list}")
        source = SpotifyCache(url="", name=name_list)
        voice_client = await source.connect_to_voice_channel(
            voice_client=voice_client, voice_channel=message.author.voice.channel
        )
        await source.play_playlist(voice_client=voice_client, message=message)
    elif comando.startswith("canta "):
        link = comando[len("canta ") :]
        source: MusicSource = None
        if "https://youtu" in link:
            source = YTSource(url=link, name="")
            voice_client = await source.connect_to_voice_channel(
                voice_client=voice_client, voice_channel=message.author.voice.channel
            )
            source.play_in(voice_client=voice_client)
        else:
            print("Unexpected link")
            await message.reply(
                "que coño acabas de mandar bro, vete a dar un paseo 🚶‍♂️🚶‍♂️🚶‍♂️"
            )
    elif comando.startswith("listas"):
        await SpotifyCache.read_list(message=message)
    elif comando.startswith("descarga "):
        params = comando[len("descarga ") :]
        params = params.split(" ")
        if len(params) != 2:
            await message.reply(
                'tienes que decirme "pichi descarga nombre-lista https://open.spotify...", el nombre de la lista no puede tener espacios'
            )
            return
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
"""


@client.event
async def on_voice_state_update(member, before, after):
    global voice_client
    voice_state = member.guild.voice_client
    if voice_state is not None and len(voice_state.channel.members) == 1:
        voice_state.stop()
        await voice_state.disconnect()


client.run(DISCORD_TOKEN)
