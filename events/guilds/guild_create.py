from interactions import listen, Client, Extension, EmbedFooter, Embed
from interactions.api.events import GuildJoin

from database.guild import GuildDB


class GuildCreate(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @listen()
    async def on_guild_create(self, event: GuildJoin):
        db = GuildDB(event.guild)
        if db.get_guild_info() is None:
            owner = await event.guild.fetch_owner()

            await db.create_guild()
            new_server_embed = Embed(
                title="Altera Tickets",
                description="Thank you for inviting Altera Tickets to your server! Below is a quick guide on setting the bot up, please don't hesitate to contact us in our [support server](https://discord.gg/alterasms) if you need any assistance!",
                color=self.client.success,
                footer=EmbedFooter(
                    text=event.bot.user.username,
                    icon_url=event.bot.user.avatar.url
                )
            ) \
                .add_field("Setup", "You can setup the bot using /setup") \
                .add_field("Adding Staff",
                           "To make staff able to answer tickets, you must let the bot know about them first. You can do this through `/addsupport <@User / @Role>` and `/addadmin <@User / @Role>`. ") \
                .add_field("Claiming",
                           "Tickets can be claimed by your staff such that other staff members cannot also reply to the ticket.json.")
            new_server_embed.set_footer(text="", icon_url="")
            await owner.send(embed=new_server_embed)


def setup(client: Client):
    GuildCreate(client)