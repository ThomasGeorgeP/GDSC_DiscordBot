from googleapiclient.discovery import build
from api_keys import YOUTUBE_API_KEY
import json
import yt_dlp
import ffmpeg
import asyncio
import discord
import re

def search_youtube(query):
    """Search YouTube and return the first video URL."""
    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)
    request = youtube.search().list(
        part="snippet",
        q=query,
        maxResults=1,  # Get only the first result
        type="video"
    )
    response = request.execute()
    
    if response["items"]:
        video_id = response["items"][0]["id"]["videoId"]
        with open("youtube_search.json",'w') as f:
            json.dump(response,f,indent=4)
        return f"https://www.youtube.com/watch?v={video_id}"
    else:
        return "No results found."

class MusicPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None  # Store the bot's current voice connection

    async def reply(self,ctx:discord.Message):
        if ctx.content.startswith("$join"):
            await self.join(ctx)
        elif ctx.content.startswith("$leave"):
            await self.leave(ctx)
        else:
            await self.play(ctx)

    async def join(self, ctx):
        """Joins the voice channel of the user."""
        if ctx.author.voice:
            channel = ctx.author.voice.channel
            self.voice_client = await channel.connect()
        else:
            await ctx.send("You need to be in a voice channel first!")

    async def leave(self, ctx):
        """Disconnects from the voice channel."""
        if self.voice_client:
            await self.voice_client.disconnect()
            self.voice_client = None
        else:
            await ctx.send("I'm not in a voice channel!")

    async def play(self, ctx:discord.Message):
        """Plays audio from a YouTube URL."""
        url=ctx.content[5:]
        self.url_pattern=r"https://{.}*"

        if not re.match(self.url_pattern,url):
            url=search_youtube(url)
        
        

        ydl_opts = {
            'format': 'bestaudio',
            'noplaylist': True
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            audio_url = info['url']
        
        if not self.voice_client:
            await self.join(ctx)
            
        self.voice_client.play(
            discord.FFmpegPCMAudio(audio_url),
            after=lambda e: print(f"Finished playing: {e}")
        )

        await ctx.channel.send(f"Now playing: {info['title']}")

