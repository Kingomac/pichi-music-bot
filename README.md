# DJ Sona Music Bot

It's a discord music bot that uses [discord.py](https://github.com/Rapptz/discord.py) and [Lavalink](#https://github.com/lavalink-devs/Lavalink)

## Commands list

- `+play`: plays any song from the supported sources (Youtube, Spotify, Soundcloud...) or if it's a query plays the first result from youtube search
- `+spotify`: plays a link from Spotify (can be played also with the `+play` command)
- `+playlist-download`: downloads a playlist from Spotify on the `cached` folder
- `+playlist`: plays a playlist from Youtube or the `cached` folder
- `+pause`
- `+resume`

## Installation (for self hosting)

Requirements:

- Python 3.10+
- Java JDK 17+ (LTS versions recommended)


Steps:

1. Clone the repo
2. `python -m pip install -r requirements.txt`
3. Create a `.env` file with the next information:
```
DISCORD_TOKEN=discord_token
SPOTIFY_CLIENT_ID=client_id
SPOTIFY_CLIENT_SECRET=client_secret
```
4. Run Lavalink using the `application.yml` config file:
   1. In a new terminal
   2. `cd lavalink`
   3. `java -jar Lavalink.jar application.yml`
5. Run the bot: `python src/main.py`

