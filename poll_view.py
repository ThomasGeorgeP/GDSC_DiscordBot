import discord
from discord.ext import commands

class PollView(discord.ui.View):
    def __init__(self, options: list, title: str = "Poll",show:bool=True):
        super().__init__(timeout=None)
        self.title = title
        self.options = options
        self.votes = {option: 0 for option in options}
        self.voters = {} 
        self.message = None 
        self.emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        self.display=show

        
        for index, option in enumerate(options):
            button = discord.ui.Button(
                label=f"{self.emojis[index]} {option}",
                style=discord.ButtonStyle.gray,
                custom_id=str(index)
            )
            button.callback = self.create_callback(option) 
            self.add_item(button)

    def create_callback(self, option):
        async def button_callback(interaction: discord.Interaction):
            """Handles button click, deletes old message, and creates a new one."""
            await interaction.response.defer() 

            user_id = interaction.user.id
            previous_vote = self.voters.get(user_id)

            
            if previous_vote and self.display:
                self.votes[previous_vote] -= 1
                if self.display:
                    await self.message.channel.send(content=f"<@{interaction.user.id}> removed their vote for {previous_vote}")
            
            
            self.votes[option] += 1
            self.voters[user_id] = option 

            
            if self.message:
                try:
                    await self.message.delete()
                except discord.NotFound:
                    pass  

           
            new_message = await interaction.channel.send(embed=self.get_poll_embed(), view=self)
            self.message = new_message 
            if self.display:
                await self.message.channel.send(content=f"<@{interaction.user.id}> voted for {option}")
        return button_callback

    def get_poll_embed(self):
        """Creates an embed with updated vote counts."""
        poll_embed = discord.Embed(
            title=self.title,
            description="📊 **Please choose among the following options:**",
            color=discord.Color.blurple()
        )
        
        poll_text = "\n".join(
            [f"{self.emojis[i]} {opt} - **{self.votes[opt]} votes**" for i, opt in enumerate(self.options)]
        )
        poll_embed.add_field(name="Options", value=poll_text, inline=False)
        
        return poll_embed

async def create_poll(channel: discord.TextChannel, title: str, options: list):
    """Function to send the poll message and store reference"""
    view = PollView(options, title)
    sent_message = await channel.send(embed=view.get_poll_embed(), view=view)
    view.message = sent_message  # Store reference so we can delete & recreate it later
