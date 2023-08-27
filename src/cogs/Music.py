# The `Music` class is a Discord bot cog that handles playing music from YouTube and Spotify, as well
# as managing the voice client and queue.
import discord
from discord.ext import commands
import wavelink
from wavelink.ext import spotify
import asyncio
from cogs.SpotifyCache import SpotifyCache


class VoiceClientConnectException(Exception):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)


class Music(commands.Cog):
    def __init__(self, bot: commands.Bot, spotify_secrets: tuple[str]) -> None:
        self.bot = bot
        self.voice_client: discord.VoiceClient = None
        self.spotify_client = spotify.SpotifyClient(
            client_id=spotify_secrets[0],
            client_secret=spotify_secrets[1],
        )
        self.message_channel: discord.abc.Messageable = None
        self.autoplay = True

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
            raise VoiceClientConnectException()
        if not ctx.voice_client:
            self.voice_client: wavelink.Player = await ctx.author.voice.channel.connect(
                cls=wavelink.Player
            )
        else:
            self.voice_client: wavelink.Player = ctx.voice_client

    @commands.command()
    async def play(self, ctx: commands.Context, *, search: str) -> None:
        """Simple play command."""
        try:
            await self.connect_voice_client(ctx)
        except VoiceClientConnectException:
            return
        self.message_channel = ctx.channel

        if search.startswith("https://open.spotify.com"):
            await self.play_spotify_song(ctx, search)
            return

        tracks: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.reply(
                f"Sorry I could not find any songs with search: `{search}`",
                ephemeral=True,
            )
            return

        track: wavelink.YouTubeTrack = tracks[0]
        if not self.voice_client.is_playing():
            await self.voice_client.play(track)
        else:
            await self.voice_client.queue.put_wait(track)

    @commands.command()
    async def spotify(self, ctx: commands.Context, *, search: str):
        try:
            await self.connect_voice_client(ctx)
        except VoiceClientConnectException:
            return
        await self.play_spotify_song(ctx, search)

    async def play_spotify_song(self, ctx: commands.Context, search: str):
        """
        The function `play_spotify_song` plays a Spotify song in a voice channel using the provided
        search query (it must be a url from Spotify).

        :param ctx: The `ctx` parameter is an instance of the `commands.Context` class, which represents
        the context in which a command is being invoked. It contains information about the command, the
        message that triggered it, the channel it was invoked in, the author who invoked it, etc
        :type ctx: commands.Context
        :param search: The `search` parameter is a string that represents the search query for a song on
        Spotify. It can be the name of the song, artist, or any other relevant information that can help
        identify the desired song
        :type search: str
        :return: nothing (None).
        """
        decoded = spotify.decode_url(search)
        if not decoded or decoded["type"] is not spotify.SpotifySearchType.track:
            await ctx.reply("esto no es de spotify bro", ephemeral=True)
            return
        tracks: list[spotify.SpotifyTrack] = await self.spotify_client._search(search)
        if not tracks:
            await ctx.reply("url rara", ephemeral=True)
            return
        track: spotify.SpotifyTrack = tracks[0]

        if not self.voice_client.is_playing():
            await self.voice_client.play(track)
        else:
            await self.voice_client.queue.put_wait(track)

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
            self.voice_client != None
            and self.voice_client.channel != None
            and len(self.voice_client.channel.members) == 1
        ):
            await self.voice_client.disconnect()

    @commands.command()
    async def autoplay(self, ctx: commands.Context, *, search: str) -> None:
        """
        The `autoplay` function connects to a voice client, searches for a track based on a given search
        query, and either plays the track immediately or adds it to the queue if there is already a
        track playing and fills the auto_queue with recommendations based on that song.

        :param ctx: The `ctx` parameter is an instance of the `commands.Context` class, which represents
        the context in which a command is being invoked. It contains information about the command
        invocation, such as the message, the channel, the author, and more
        :type ctx: commands.Context
        :param search: The `search` parameter is a string that represents the search query for the
        desired song or track. It is used to search for tracks on YouTube using the
        `wavelink.YouTubeTrack.search()` method
        :type search: str
        :return: The function does not have a return statement, so it does not explicitly return
        anything.
        """
        try:
            await self.connect_voice_client(ctx)
        except VoiceClientConnectException:
            return
        self.message_channel = ctx.channel

        tracks: list[wavelink.YouTubeTrack] = await wavelink.YouTubeTrack.search(search)
        if not tracks:
            await ctx.reply(
                f"Sorry I could not find any songs with search: `{search}`",
                ephemeral=True,
            )
            return

        track: wavelink.YouTubeTrack = tracks[0]
        if not self.voice_client.is_playing():
            await self.voice_client.play(track, populate=True)
        else:
            await self.voice_client.queue.put_wait(track)
        await asyncio.sleep(10)
        print(list(self.voice_client.auto_queue))
        await ctx.send(list(self.voice_client.auto_queue))

    @commands.command()
    async def playlist(self, ctx: commands.Context, *, search: str):
        """
        The `playlist` command is used to search for and play a playlist, either from a Spotify
        link or by searching for a YouTube playlist.

        :param ctx: The `ctx` parameter is an instance of the `commands.Context` class, which represents the
        context in which a command is being invoked. It contains information about the command invocation,
        such as the message, the channel, the author, and more
        :type ctx: commands.Context
        :param search: The `search` parameter is a string that represents the search query for the playlist.
        It can be either a URL of a Spotify playlist or a search query for a YouTube playlist
        :type search: str
        :return: The code is returning a list of tracks in the voice client's queue.
        """
        try:
            await self.connect_voice_client(ctx)
        except VoiceClientConnectException:
            return
        self.message_channel = ctx.channel

        if search.startswith("https://open.spotify.com/playlist"):
            if SpotifyCache.is_playlist_cached(search):
                tracks = SpotifyCache.get_tracks(search)
                async for i in tracks:
                    await self.voice_client.queue.put_wait(i)
                self.voice_client.queue.shuffle()
                await self.voice_client.play(self.voice_client.queue.pop())
            else:
                await ctx.reply("playlist no descargada")
            return

        results: wavelink.YouTubePlaylist = await wavelink.YouTubePlaylist.search(
            search
        )
        if not results:
            await ctx.reply("playlist no encontrada bro", ephemeral=True)
            return

        playlist = results
        for i in playlist.tracks:
            await self.voice_client.queue.put_wait(i)
        self.voice_client.queue.shuffle()
        await self.voice_client.play(self.voice_client.queue.pop())
        await ctx.reply(list(self.voice_client.queue))

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        """
        This event triggers when a track ends and it makes sure a song is played if there are any in
        the queue (autoplay in some cases does not work)

        :param payload: The `payload` parameter is an instance of the `wavelink.TrackEventPayload`
        class. It contains information about the track that has ended, such as the track itself, the
        player that played the track, and the reason for the track ending
        :type payload: wavelink.TrackEventPayload
        """
        if not self.voice_client.is_playing() and len(self.voice_client.queue) > 0:
            await self.voice_client.play(self.voice_client.queue.pop(), populate=True)
        for i in self.voice_client.auto_queue:
            print(f"autoqueue:" + i.name)

    @commands.command()
    async def pause(self, ctx: commands.Context):
        if self.voice_client != None and self.voice_client.is_playing():
            await self.voice_client.pause()

    @commands.command()
    async def resume(self, ctx: commands.Context):
        if self.voice_client != None and self.voice_client.is_paused():
            await self.voice_client.resume()
