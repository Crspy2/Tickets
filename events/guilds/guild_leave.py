import asyncio

from interactions import listen, Client, Extension
from interactions.api.events import GuildLeft

from database.guild import GuildDB


class GuildLeave(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @listen()
    async def on_guild_left(self, event: GuildLeft):
        pass
        # await asyncio.sleep(1296000)
        # db = GuildDB(event.guild)
        # db.delete_guild()


def setup(client: Client):
    GuildLeave(client)
