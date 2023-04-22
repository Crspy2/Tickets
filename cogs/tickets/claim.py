from interactions import Extension, Client, SlashContext, OptionType, User, Embed, slash_command, slash_option, \
    EmbedFooter
from database.guild import GuildDB
from database.ticket import TicketDB


class Claim(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="claim",
        description="Assigns a single staff member to a ticket"
    )
    async def claim(self, ctx: SlashContext):
        guild_db = GuildDB(ctx.guild)
        settings = guild_db.get_guild_info()
        tickets = TicketDB(ctx.guild)
        ticket_info = tickets.get_ticket_info(ctx.channel)

        author_roles = []
        for role in ctx.author.roles:
            author_roles.append(str(role.id))

        has_admin_roles = set(author_roles).intersection(set(settings['admins']))
        if not guild_db.is_admin(ctx.author.id):
            if not has_admin_roles:
                no_perms = Embed(
                    title="Error",
                    description="You do not have permissions for this command!",
                    color=self.client.error,
                    footer=EmbedFooter(
                        text="Powered by altera.vip",
                        icon_url=self.bot.user.avatar.url
                    )
                )
                return await ctx.send(embed=no_perms, ephemeral=True)

        if ticket_info['claimed']:
            alr_claimed = Embed(
                title="Error",
                description="This ticket has already been claimed!",
                color=self.client.error,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            return await ctx.send(embed=alr_claimed, ephemeral=True)


        tickets.update_ticket_info(ctx.channel, **{'claimed': True}, **{'claimed_by': ctx.author.id})


def setup(client: Client):
    Claim(client)
