import os
import discord
from discord.ext import commands
from dotenv import load_dotenv
import wavelink
from cogs.Music import Music

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DISCORD_GUILDS = os.getenv("DISCORD_GUILDS").strip("[]").split(", ")
CALL_NAME = "sona" + " "
print(DISCORD_GUILDS)


class Bot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True

        super().__init__(intents=intents, command_prefix="+")

    async def on_ready(self) -> None:
        print(f"Logged in {self.user} | {self.user.id}")

    async def setup_hook(self) -> None:
        # Wavelink 2.0 has made connecting Nodes easier... Simply create each Node
        # and pass it to NodePool.connect with the client/bot.
        node: wavelink.Node = wavelink.Node(
            uri="http://localhost:2333", password="youshallnotpass"
        )
        await wavelink.NodePool.connect(client=self, nodes=[node])
        await self.add_cog(Music(self))


bot = Bot()

bot.run(DISCORD_TOKEN)
