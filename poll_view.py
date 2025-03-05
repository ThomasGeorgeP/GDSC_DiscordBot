import discord
from discord.ext import commands

class PollView(discord.ui.View):
    def __init__(self, options: list, title: str = "Poll"):
        super().__init__(timeout=None)
        self.title = title
        self.options = options
        self.votes = {option: 0 for option in options}  # Track votes
        self.voters = {}  # Track who voted for what
        self.message = None  # Store poll message reference
        self.emojis = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣", "6️⃣", "7️⃣", "8️⃣", "9️⃣", "🔟"]

        # Dynamically create buttons
        for index, option in enumerate(options):
            button = discord.ui.Button(
                label=f"{self.emojis[index]} {option}",
                style=discord.ButtonStyle.gray,
                custom_id=str(index)
            )
            button.callback = self.create_callback(option)  # Assign callback dynamically
            self.add_item(button)

    def create_callback(self, option):
        async def button_callback(interaction: discord.Interaction):
            """Handles button click, deletes old message, and creates a new one."""
            await interaction.response.defer()  # Acknowledge interaction

            user_id = interaction.user.id
            previous_vote = self.voters.get(user_id)

            # Remove old vote if exists
            if previous_vote:
                self.votes[previous_vote] -= 1

            # Register new vote
            self.votes[option] += 1
            self.voters[user_id] = option  # Update voter's choice

            # Delete old message if it exists
            if self.message:
                try:
                    await self.message.delete()
                except discord.NotFound:
                    pass  # Ignore if message was already deleted

            # Send a new poll message with updated votes
            new_message = await interaction.channel.send(embed=self.get_poll_embed(), view=self)
            self.message = new_message  # Update reference to the new message

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
