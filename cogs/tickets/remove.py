from interactions import Extension, Client, SlashContext, OptionType, User, Embed, slash_command, slash_option, \
    EmbedFooter, Permissions

from database.ticket import TicketDB
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
        if TicketDB(ctx.guild).get_ticket_info(ctx.channel) is None:
            not_a_ticket = Embed(
                title="Error",
                description="This is not a ticket channel",
                color=self.bot.error,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            return await ctx.send(embed=not_a_ticket, ephemeral=True)

        if GuildDB(ctx.guild).is_admin(user.id) or GuildDB(ctx.guild).is_support(user.id):
            is_staff = Embed(
                title="Error",
                description="You cannot remove staff from a ticket",
                color=self.bot.error,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            return await ctx.send(embed=is_staff, ephemeral=True)

        if user is ctx.guild.get_owner():
            is_owner = Embed(
                title="Error",
                description="You cannot remove staff from a ticket",
                color=self.bot.error,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            return await ctx.send(embed=is_owner, ephemeral=True)
        if user not in ctx.channel.humans or user in ctx.channel.bots:
            alr_in_ticket = Embed(
                title="Error",
                description="User not in ticket",
                color=self.bot.error,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            return await ctx.send(embed=alr_in_ticket, ephemeral=True)

        await ctx.channel.set_permission(user, view_channel=False)
        user_added = Embed(
            title="Remove",
            description=f"{ctx.author.mention} has been removed from {ctx.channel.mention}",
            color=self.bot.success,
            footer=EmbedFooter(
                text="Powered by altera.vip",
                icon_url=self.bot.user.avatar.url
            )
        )

        await ctx.send(embed=user_added)


def setup(client: Client):
    Admin(client)
