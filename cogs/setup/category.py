from interactions import Extension, Client, SlashContext, subcommand, slash_option, OptionType, \
    Embed, GuildCategory

from database.guild import GuildDB


class Limit(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @subcommand(
        base="set",
        name="limit",
        description="Easily configure the ticket.json limit for a user",
    )
    @slash_option(
        name="limit",
        description="The maximum amount of tickets a user can have open simultaneously",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value=1
    )
    async def category(self, ctx: SlashContext, category: GuildCategory):
        await ctx.defer(ephemeral=True)
        db = GuildDB(ctx.guild)
        settings = db.get_guild_info()
        author_roles = []
        for role in ctx.author.roles:
            author_roles.append(str(role.id))

        has_admin_roles = set(author_roles).intersection(set(settings['admins']))

        # Check if interaction author is an admin
        if not db.is_user_admin(ctx.author.user.id):
            if not has_admin_roles:
                no_perms = Embed(
                    title="Error",
                    description="You do not have permissions for this command!",
                    color=self.client.error
                )
                return await ctx.send(embed=no_perms)

        category = {'default_category': category.id}
        db.update_guild_info(**category)

        confirm_embed = Embed(
            title="Setup",
            description=f"The ticket.json channel category has been changed to `{category.name}`",
            color=self.client.success
        )
        return await ctx.send(embed=confirm_embed)


def setup(client: Client):
    Limit(client)