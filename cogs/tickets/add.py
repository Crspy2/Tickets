from interactions import Extension, Client, SlashContext, OptionType, User, Embed, slash_command, slash_option, \
    EmbedFooter

from database.ticket import TicketDB


class Admin(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="add",
        description="Adds a user to a ticket"
    )
    @slash_option(
        name="user",
        description="User to add to the ticket",
        required=True,
        opt_type=OptionType.USER
    )
    async def add(self, ctx: SlashContext, user: User):
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

        if user in ctx.channel.humans:
            alr_in_ticket = Embed(
                title="Error",
                description="User already in ticket",
                color=self.bot.error,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            return await ctx.send(embed=alr_in_ticket, ephemeral=True)

        await ctx.channel.set_permission(user, send_messages=True, embed_links=True, attach_files=True,
                                         add_reactions=True, read_message_history=True,
                                         use_application_commands=True, view_channel=True)

        user_added = Embed(
            title="Add",
            description=f"{user.mention} has been added to {ctx.channel.mention}",
            color=self.bot.success,
            footer=EmbedFooter(
                text="Powered by altera.vip",
                icon_url=self.bot.user.avatar.url
            )
        )
        msg = await ctx.send(content=user.mention, embed=user_added)
        await msg.edit(content="", embed=user_added)


def setup(client: Client):
    Admin(client)
