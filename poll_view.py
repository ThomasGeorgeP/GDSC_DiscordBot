import discord
from discord.ext import commands

class PollView(discord.ui.View):
    def __init__(self,options: list,title:str="Poll"):
        super().__init__(timeout=None)
        self.title = title
        self.options = options
        self.votes = {option: 0 for option in options}  # Track votes
        self.message = None  # Store poll message reference
        self.emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]
        self.voters=[]

        # Dynamically create buttons
        for index, option in enumerate(options):
            button = discord.ui.Button(label=f"{self.emojis[index]} {option}", style=discord.ButtonStyle.gray, custom_id=str(index))
            button.callback = self.create_callback(option)
            self.add_item(button)

    def create_callback(self, option):
        async def button_callback(interaction: discord.Interaction):
            """Handles button click and updates the poll message."""
            if interaction.user.id not in self.voters:
                self.votes[option] += 1  # Increase vote count

                # Delete old poll message
                if self.message:
                    try:
                        await self.message.delete()
                    except discord.NotFound:
                        pass 

                
                new_message = await interaction.channel.send(embed=self.get_poll_embed(), view=self)
                self.message = new_message
                self.voters.append(interaction.user.id)
            else:
                await interaction.response.send_message(content="You already voted! ",ephemeral=True)
        return button_callback

    def get_poll_embed(self):
        """Creates an embed with updated vote counts."""
        poll_embed = discord.Embed(
            title=self.title,
            description="📊 **Please choose among the following options:**",
            color=discord.Color.blurple()
        )
        
        poll_text = "\n".join([f"{self.emojis[i]} {opt} - **{self.votes[opt]} votes**" for i, opt in enumerate(self.options)])
        poll_embed.add_field(name="Options", value=poll_text, inline=False)
        
        return poll_embed
