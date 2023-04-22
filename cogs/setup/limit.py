from interactions import Extension, Client, SlashContext, subcommand, slash_option, OptionType, \
    Embed

from database.guild import GuildDB


class Category(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @subcommand(
        base="set",
        name="limit",
        description="Sets the max amount of tickets a user can have open simultaneously",
    )
    @slash_option(
        name="number",
        description="The max amount of tickets!",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value=1
    )
    async def limit(self, ctx: SlashContext, number: int):
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
                    color=self.client.error
                )
                return await ctx.send(embed=no_perms)

        ticket_limit = {'limit': number}
        db.update_guild_info(**ticket_limit)

        confirm_embed = Embed(
            title="Setup",
            description=f"The ticket limit has been updated to `{number}`",
            color=self.client.success
        )
        return await ctx.send(embed=confirm_embed)


def setup(client: Client):
    Category(client)