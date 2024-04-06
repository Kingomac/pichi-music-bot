import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import wavelink
from cogs import YoutubeCog, WavelinkSourceCog, YoutubeMusicCog

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
        await wavelink.Pool.connect(client=self, nodes=[node])
        await self.add_cog(YoutubeCog(self))
        await self.add_cog(YoutubeMusicCog(self))


bot = Bot()

bot.run(DISCORD_TOKEN)
