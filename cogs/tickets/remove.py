from interactions import Extension, Client, SlashContext, OptionType, User,\
    slash_command, slash_option

from database.guild import GuildDB

class Admin(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="remove",
        description="Removes a user from a ticket.json"
    )
    @slash_option(
        name="user",
        description="User to remove from current ticket.json",
        required=True,
        opt_type=OptionType.USER
    )
    async def remove(self, ctx: SlashContext, user: User):
        await ctx.send(f"TODO\nYou passed {user} as your option!", ephemeral=True)



def setup(client: Client):
    Admin(client)