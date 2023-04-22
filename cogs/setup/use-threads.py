from interactions import Extension, Client, SlashContext, subcommand, slash_option, OptionType, \
    Embed, GuildChannel, EmbedFooter

from database.guild import GuildDB


class Limit(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @subcommand(
        base="set",
        name="use_threads",
        description="Easily configure the ticket.json type",
    )
    @slash_option(
        name="use_threads",
        description="Whether or not private threads should be used for tickets",
        required=True,
        opt_type=OptionType.BOOLEAN,
    )
    @slash_option(
        name="thread_notification_channel",
        description="The channel to send thread notifications in!",
        required=False,
        opt_type=OptionType.CHANNEL,
    )
    async def threads(self, ctx: SlashContext, use_threads: bool, thread_notification_channel: GuildChannel = None):
        await ctx.defer(ephemeral=True)
        db = GuildDB(ctx.guild)
        settings = db.get_guild_info()

        author_roles = []
        for role in ctx.author.roles:
            author_roles.append(str(role.id))

        has_admin_roles = set(author_roles).intersection(set(settings['admins']))

        # Check if interaction author is an admin
        if not db.is_admin(ctx.author.id):
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
                return await ctx.send(embed=no_perms)

        if use_threads and thread_notification_channel is None:
            missing_arg = Embed(
                title="Missing Argument",
                description="You must provide a ticket notification channel!",
                color=self.client.error,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            return await ctx.send(embed=missing_arg)

        # use_threads = {'use_threads': ctx.kwargs['use_threads']}
        use_threads = {'threads.use_threads': use_threads, 'threads.thread_notification_channel': thread_notification_channel.id}
        db.update_guild_info(**use_threads)

        confirm_embed = Embed(
            title="Setup",
            description=f"Thread mode has been {'enabled' if ctx.kwargs['use_threads'] else 'disabled'}",
            color=self.client.success,
            footer=EmbedFooter(
                text="Powered by altera.vip",
                icon_url=self.bot.user.avatar.url
            )
        )
        return await ctx.send(embed=confirm_embed)


def setup(client: Client):
    Limit(client)
