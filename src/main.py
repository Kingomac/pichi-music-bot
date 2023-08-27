import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import wavelink
from cogs.Music import Music
from cogs.SpotifyCache import SpotifyCache

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET")


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, command_prefix="+")

    async def on_ready(self) -> None:
        print(f"Logged in {self.user} | {self.user.id}")

    async def setup_hook(self) -> None:
        node: wavelink.Node = wavelink.Node(
            uri="http://localhost:2333", password="youshallnotpass"
        )
        await wavelink.NodePool.connect(client=self, nodes=[node])
        await self.add_cog(
            Music(self, spotify_secrets=(SPOTIFY_CLIENT_ID, SPOTIFY_CLIENT_SECRET))
        )
        await self.add_cog(SpotifyCache(self))


bot = Bot()

bot.run(DISCORD_TOKEN)
