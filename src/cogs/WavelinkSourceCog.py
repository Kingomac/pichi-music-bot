from discord.ext import commands
import discord
import wavelink

class WavelinkSourceCog(commands.Cog):
    def __init__(self, bot: commands.Bot, track_source: wavelink.TrackSource) -> None:
        self.bot = bot
        self._track_source = track_source
        self._message_channel: discord.abc.Messageable = None
        self._voice_client: wavelink.Player = None

    @property
    def track_source(self):
        return self._track_source
    
    async def connect_voice_client(self, ctx: commands.Context):
        """
        The function connects the voice client to a voice channel if the author is in a voice channel.

        :param ctx: The `ctx` parameter is an instance of the `commands.Context` class, which represents
        the context in which a command is being invoked. It contains information about the message, the
        command, the author, the channel, and other relevant details. In this case, it is used to check
        if the
        :type ctx: commands.Context
        """
        if ctx.author.voice == None:
            await ctx.reply("a ver y donde te lo pincho bro", ephemeral=True)
            return
        self._voice_client: wavelink.Player = await ctx.author.voice.channel.connect(
            cls=wavelink.Player
        )
    
    async def _play(self, ctx: commands.Context, *, search: str) -> None:
        """Simple play command."""
        if not ctx.voice_client:
            await self.connect_voice_client(ctx)
        
        self._message_channel = ctx.channel

        tracks: wavelink.Search = await  wavelink.Playable.search(search, source=self.track_source)
        if not tracks:
            await ctx.reply(
                "marrano qué buscas",
                ephemeral=True,
            )
            return

        track: wavelink.Playable = tracks[0]
        print(track)
        print(f"{self._voice_client.playing=}")
        #if not self._voice_client.playing:
        await self._voice_client.queue.put_wait(track)
        if not self._voice_client.playing:
            await self._voice_client.play(await self._voice_client.queue.get_wait(), volume=100)
        #else:
        #    await self._voice_client.queue.put_wait(track)

    async def _on_voice_state_update(
        self,
        member: discord.Member,
        before: discord.VoiceState,
        after: discord.VoiceState,
    ):
        """
        The function checks if the bot is alone in a voice chat, if so, it disconnects

        :param member: The `member` parameter represents the member whose voice state has been updated.
        It is of type `discord.Member`
        :type member: discord.Member
        :param before: The `before` parameter is the `discord.VoiceState` object representing the voice
        state of the member before the update. It contains information such as the channel the member
        was in before the update, whether they were muted or deafened, etc
        :type before: discord.VoiceState
        :param after: The `after` parameter is an instance of the `discord.VoiceState` class and
        represents the updated voice state of the member after the change. It contains information such
        as the channel the member is currently in, whether they are muted or deafened, etc
        :type after: discord.VoiceState
        """
        if (
            self._voice_client != None
            and self._voice_client.channel != None
            and len(self._voice_client.channel.members) == 1
        ):
            await self._voice_client.disconnect()
    
    async def _disconnect(self, ctx: commands.Context) -> None:
        """Simple disconnect command."""
        if ctx.voice_client:
            await ctx.voice_client.disconnect()
            self._message_channel = None
            self._voice_client = None
        else:
            await ctx.reply("no estoy en un canal de voz", ephemeral=True)

    async def _on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        """
        This event triggers when a track ends and it makes sure a song is played if there are any in
        the queue (autoplay in some cases does not work)

        :param payload: The `payload` parameter is an instance of the `wavelink.TrackEventPayload`
        class. It contains information about the track that has ended, such as the track itself, the
        player that played the track, and the reason for the track ending
        :type payload: wavelink.TrackEventPayload
        """
        if not self._voice_client:
            return
        if not self._voice_client.playing and len(self._voice_client.queue) > 0:
            await self._voice_client.play(await self._voice_client.queue.get_wait())
        for i in self._voice_client.auto_queue:
            print(f"autoqueue:" + i.name)            