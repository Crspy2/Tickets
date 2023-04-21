import asyncio

from interactions import Extension, Client, SlashContext, Embed, \
    Button, ButtonStyle, slash_command
from interactions.api.events import Component

from database.guild import GuildDB


class Open(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="test",
        description="test"
    )
    async def open(self, ctx: SlashContext):
        await ctx.send("Hello")



def setup(client: Client):
    Open(client)
