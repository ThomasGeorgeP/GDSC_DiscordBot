import discord
from discord.ext import commands
from discord import app_commands
from client_class import myClient
from api_keys import DISCORD_API_KEY

from google import genai

discord_intents=discord.Intents.default()
discord_intents.message_content=True
discord_intents.members=True
client=myClient(command_prefix="$",intents=discord_intents)



server_id=discord.Object(1346101662590173305)

client.run(DISCORD_API_KEY)