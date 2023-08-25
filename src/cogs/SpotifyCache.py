import discord
from discord.ext import commands
import os
import subprocess
import wavelink
import asyncio


class SpotifyCache(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def download_playlist(search: str):
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
