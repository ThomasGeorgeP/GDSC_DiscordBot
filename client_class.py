import discord
from discord.ext import commands
from discord import app_commands
from gemini import gemini
from poll_view import PollView
import json
from reminders import timekeeper,REMINDER_FILE,convert_to_timestamp,seconds_from_now
import time
import asyncio
from music_player import MusicPlayer
class myClient(commands.Bot):
    
    
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.gemini=gemini(self)
        self.server_id=discord.Object(1346101662590173305)
        self.slash_commands()
        self.poll_message=False
        self.poll_id=None
        self.timekeeper=timekeeper(self)
        self.music_player=MusicPlayer(self)

    async def on_ready(self):
    
        print(f'Logged on as {self.user}! ')
        try:
            await self.tree.sync(guild=self.server_id)
        except:
            print("error")
        if self.timekeeper.reminders:
            await self.timekeeper.remind()
        
    async def on_message(self,message:discord.Message):
        
        if message.author==self.user and self.poll_message:
            self.poll_id=discord.Object(message.id)
            self.poll_message=False
        elif message.author==self.user:
            await self.catch_own_messages(message=message)

        if message.content.startswith("$status"):
            await message.channel.send(f"Bot is Up and running!")
        elif message.content.startswith("$help"):
            await message.channel.send(f'''
                            $ai <prompt> - generates prompt
                            $summarize - (reply to the message you want to summarize with $summarize
                            Slash Commands:
                                /create_poll <options seperated by commas> <title(optional)> <show(bool) for anonymous voting>
                                /rickroll -self explanatory
                                /create_reminder <dd-mm-yyyy hour:minutes in 24 hour format>)''')
        elif message.content.startswith("$ai") or message.content.startswith("$summarize") or message.content.startswith("$tellmore"):
            await self.gemini.reply(message)
        elif message.content.startswith("$join") or message.content.startswith("$leave") or message.content.startswith("$play"):
            await self.music_player.reply(message)
        else:
            pass
            

    async def on_message_edit(self,before,after):
        #print(type(before))
        #print(type(client))
        if before.author==self.user:
            return None
        else:
            await after.channel.send(f"Message edited from {before.content} to {after.content}")

    async def on_member_join(self,member: discord.Member):
        text = self.gemini.gen(f"Tell me a short,fun and clever welcoming sentence for the name. {member.name}. Give me just the introduction. ")
        #await member.channel.send(response.text+"@"+member.name)
        for channel in member.guild.text_channels:
            if channel.name=="welcome-chat":
                await channel.send(text+"<"+"@"+str(member.id)+">")
                break
        else:
            new_channel = await member.guild.create_text_channel(name="welcome chat")

            await new_channel.send(text+"<"+"@"+str(member.id)+">")

    async def remind(self,parameters :dict):
        
        reminder_embed=discord.Embed(title="REMINDER",description=parameters["description"])
        reminder_embed.set_image(url=r"https://i.pinimg.com/736x/fc/ec/af/fcecafe79df247974cea7aa03d4b691a.jpg")
        reminder_embed.add_field(name="User",value=f"<@{parameters["user"]}>!")
        channel=await self.fetch_channel(parameters["channel_id"])
        #message=await channel.fetch_message(parameters["message_id"])
        await channel.send(content=f"<@{parameters["user"]}>!",embed=reminder_embed)

    async def catch_own_messages(self,message:discord.Message):
        
        if message.content=="Reminder created successfully!":
            await asyncio.sleep(5)
            self.params["message_id"]=message.id
            await self.new_timekeeper()

    async def new_timekeeper(self):
        try:
            with open(REMINDER_FILE) as f:
                reminders:list=json.load(f)
                reminders.append(self.params)
        except:
            reminders=[]
            reminders.append(self.params)
        with open(REMINDER_FILE,'w') as f:
            json.dump(reminders,f,indent=3)
        del self.timekeeper
        self.timekeeper=timekeeper(self)
        await self.timekeeper.remind()

    def slash_commands(self):
        
        @self.tree.command(name="helloo",description="Bot Says Hi! ",guild=self.server_id)
        async def helloo(interaction: discord.Interaction):
            await interaction.response.send_message("Hi there! ")

        @self.tree.command(name="create_poll",description="Create a poll! Seperate the different options by using commas!. maximum ten options",guild=self.server_id)
        async def poll(interaction:discord.Interaction,options:str,title:str="Poll",show:bool=True):
            options=options.split(",")[:10]
            global option_choices
            option_choices={i:0 for i in options}
            
            poll_embed=discord.Embed(title=title,description="Please Choose among the following",color=discord.Color.blurple())

            emoji=":one: :two: :three: :four: :five: :six: :seven: :eight: :nine:: keycap_ten:".split()
            poll_text=""
            for i in range(len(options)):
                poll_text+=emoji[i]+" : "+options[i]+" : "+str(option_choices[options[i]])+"\n"
            poll_embed.add_field(name="Options: ",value=poll_text)
            await interaction.response.send_message(embed=poll_embed,view=PollView(options,show))
            self.poll_message=True

        @self.tree.command(name="rickroll",description="The age old prank!",guild=self.server_id)
        async def rickroll(interaction:discord.Interaction):
            embed = discord.Embed(title="rickroll",url=r"https://youtu.be/dQw4w9WgXcQ?si=TSz-6luaFslQEbuV",description="jabait",color=discord.Color.red())
            embed.set_thumbnail(url=r"https://s.yimg.com/ny/api/res/1.2/Onq1adoghZAHhpsXXmF8Pw--/YXBwaWQ9aGlnaGxhbmRlcjt3PTEyNDI7aD05MzE-/https://media.zenfs.com/en/insider_articles_922/c6ce8d0b9a7b28f9c2dee8171da98b8f")
            await interaction.response.send_message(embed=embed)

        @self.tree.command(name="create_reminder",description="Creates Reminder and Pings user. ",guild=self.server_id)
        async def createreminder(interaction:discord.Interaction,datetime:str,description:str=""):
            try:
                timestamp=convert_to_timestamp(datetime)
            except:
                await interaction.response.send_message("Invalid format")
                return
            '''
            {
        "user":86497869287942378,
        "descripton":"Reminder",
        "due_time":"dd-mm-yyyy hh:mm",
        "time_till_reminder":2386748724.328467,
        "message_id":932874928379,
        "channel_id":3908247002323072374347
            }'''    
            if timestamp>time.time():
                rem_embed=discord.Embed(title="Reminder",description=f"Reminder created for {datetime}")
                rem_embed.add_field(name="User",value=f"<@{interaction.user.id}>")

                if description!='':
                    rem_embed.add_field(name="Description",value=description)
                await interaction.response.send_message(content="Reminder created successfully!",embed=rem_embed)
                self.params={"user":interaction.user.id,"description":description,"due_time":datetime,"time_till_reminder":timestamp,"channel_id":interaction.channel.id}
            else:
                await interaction.response.send_message("Time given is in the past! ")