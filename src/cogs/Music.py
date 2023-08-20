import discord
from discord.ext import commands
import wavelink


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot
        self.voice_client: discord.VoiceClient = None

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        """Simple play command."""

        if not ctx.voice_client:
            self.voice_client: wavelink.Player = await ctx.author.voice.channel.connect(
                cls=wavelink.Player
            )
        else:
            self.voice_client: wavelink.Player = ctx.voice_client

        tracks: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.send(f"Sorry I could not find any songs with search: `{search}`")
            return

        track: wavelink.YouTubeTrack = tracks[0]
        await self.voice_client.play(track)

    @commands.command()
    async def disconnect(self, ctx: commands.Context) -> None:
        """Simple disconnect command.
        This command assumes there is a currently connected Player.
        """
        vc: wavelink.Player = ctx.voice_client
        await vc.disconnect()

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        if (
            self.voice_client != None
            and self.voice_client.channel != None
            and len(self.voice_client.channel.members) == 1
        ):
            await self.voice_client.disconnect()
