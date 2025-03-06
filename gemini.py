from api_keys import GEMINI_API_KEY
from google import genai
import discord

class gemini(genai.Client):

    def __init__(self,bot,api_key=GEMINI_API_KEY) ->None:
        super().__init__(api_key=api_key)
        self.bot=bot

    def gen(self,text:str) -> str:
        self.response=self.models.generate_content(model="gemini-2.0-flash", contents=text)
        return self.response.text

    async def reply(self,message:discord.Message):
        if message.content.startswith("$ai"):
            text= self.gen(message.content[3:])
            if len(text)>1999:
                for i in range(0,len(text),1900):
                    await message.channel.send(text[i:i+1900])
            else:
                await message.channel.send(text)

        elif message.content.startswith("$summarize"):
            long_text= await message.channel.fetch_message(message.reference.message_id)
            text=self.gen("Summarize the following entered text to few lines:\n"+long_text.content)
            await message.channel.send(text)