from cogs import WavelinkSourceCog
import discord
from discord.ext import commands
import wavelink


class SoundCloudCog(WavelinkSourceCog):
    def __init__(self, bot: commands.Bot) -> None:
        super().__init__(bot, wavelink.TrackSource.SoundCloud)

    @commands.command()
    async def sc(self, ctx: commands.Context, *, search: str) -> None:
        try:
            await self._play(ctx, search=search)
        except Exception as e:
            print("Error:", e)

    @commands.Cog.listener()
    async def on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ) -> None:
        await self._on_voice_state_update(member, before, after)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        await self._on_wavelink_track_end(payload)

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, payload: wavelink.TrackExceptionEventPayload):
        print("wavelink exception:", payload.exception)

    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, payload: wavelink.TrackStuckEventPayload):
        print("wavelink stuck", payload.exception)

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        print("Start:", payload.track)
