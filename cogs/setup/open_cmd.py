from interactions import Extension, Client, SlashContext, subcommand, slash_option, OptionType, \
    Embed, GuildChannel

from database.guild import GuildDB


class Limit(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @subcommand(
        base="set",
        name="open_command",
        description="Whether or not the open command can be used in this server",
    )
    @slash_option(
        name="enable_command",
        description="Whether or not the command should be usable in this server!",
        required=True,
        opt_type=OptionType.BOOLEAN,
    )
    async def threads(self, ctx: SlashContext, enable_command: bool):
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

        # use_threads = {'use_threads': ctx.kwargs['use_threads']}
        open_command = {'disable_open_command': enable_command}
        db.update_guild_info(**open_command)

        confirm_embed = Embed(
            title="Setup",
            description=f"The `/open` command has been {'enabled' if enable_command else 'disabled'} for this server!",
            color=self.client.success
        )
        return await ctx.send(embed=confirm_embed)


def setup(client: Client):
    Limit(client)
