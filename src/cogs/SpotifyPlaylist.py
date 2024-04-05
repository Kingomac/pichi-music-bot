# The `SpotifyCache` class is a Discord bot cog that allows users to download and cache Spotify
# playlists, and provides methods to check if a playlist is already cached and retrieve the tracks
# from a cached playlist.
from discord.ext import commands
import os
import wavelink
import asyncio


class SpotifyCache(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def download_playlist(search: str):
        """
        The function `download_playlist` downloads a Spotify playlist using the spotdl library and saves
        it in a directory with its id as name.

        :param search: The `search` parameter is a string that represents the name or URL of the
        playlist you want to download
        :type search: str
        :return: the return code of the subprocess execution.
        """
        if not os.path.exists("cached"):
            os.mkdir("cached")
        playlist_id = SpotifyCache.get_spotify_playlist_id(search)
        if not os.path.exists(f"cached/{playlist_id}"):
            os.mkdir(f"cached/{playlist_id}")
        result = await asyncio.create_subprocess_exec(
            "python",
            "-m",
            "spotdl",
            "--format",
            "ogg",
            "--output",
            f"cached/{playlist_id}",
            "sync",
            search,
            "--save-file",
            f"cached/{playlist_id}/syncfile.sync.spotdl",
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )
        stdout, stderr = await result.communicate()
        print(
            f"download ended with code {result.returncode} and stdout: {stdout} and stderr: {stderr}"
        )
        return result.returncode

    @commands.command(aliases=["playlist-download"])
    async def playlist_download(self, ctx: commands.Context, *, search: str):
        await ctx.send("a sus ordenes mi capitan")
        res = await SpotifyCache.download_playlist(search)
        if res == 0:
            await ctx.send(
                "lista descargada, puedes actualizarla usando de nuevo este comando 😉"
            )
        else:
            await ctx.send(f"f error {res}")

    @staticmethod
    def is_playlist_cached(search: str):
        if search.startswith("https://open.spotify"):
            return os.path.exists(
                f"cached/{SpotifyCache.get_spotify_playlist_id(search)}"
            )
        return os.path.exists(f"cached/{search}")

    @staticmethod
    def get_spotify_playlist_id(url: str):
        return url.split("/")[4].split("?")[0]

    @staticmethod
    async def get_tracks(playlist_id: str):
        if playlist_id.startswith("https://open.spotify"):
            playlist_id = SpotifyCache.get_spotify_playlist_id(playlist_id)
        for i in os.listdir(f"cached/{playlist_id}"):
            if not i.endswith(".ogg"):
                continue
            tracks = await wavelink.tracks.GenericTrack.search(
                f"{os.getcwd()}/cached/{playlist_id}/{i}"
            )
            yield tracks.pop()
