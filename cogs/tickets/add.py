from interactions import Extension, Client, SlashContext, OptionType, User, Role, Embed, \
    Button, ButtonStyle, slash_command, slash_option, listen
from interactions.api.events import Component

from database.guild import GuildDB


class Admin(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="add",
        description="Adds a user to a ticket.json"
    )
    @slash_option(
        name="user",
        description="User to add to the ticket.json",
        required=True,
        opt_type=OptionType.USER
    )
    async def add(self, ctx: SlashContext, user: User):
        print(ctx.guild.premium_tier)
        await ctx.send(f"TODO\nYou passed {user} as your option!", ephemeral=True)



def setup(client: Client):
    Admin(client)