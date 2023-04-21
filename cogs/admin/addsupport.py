from interactions import Extension, Client, SlashContext, OptionType, User, Role, Embed, \
    Button, ButtonStyle, slash_command, slash_option

from database.guild import GuildDB


class AddAdmin(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="addsupport",
        description="Grants a user or role admin privileges"
    )
    @slash_option(
        name="user_or_role",
        description="User or role to apply the permissions to",
        required=True,
        opt_type=OptionType.MENTIONABLE
    )
    async def addsupport(self, ctx: SlashContext, user_or_role: User | Role):
        await ctx.defer(ephemeral=True)
        db = GuildDB(ctx.guild)
        settings = db.get_guild_info()
        admins = settings['admins']

        author_roles = []
        for role in ctx.author.roles:
            author_roles.append(str(role.id))

        has_admin_roles = set(author_roles).intersection(set(admins))

        # Check if interaction author is an admin
        if not db.is_user_admin(ctx.author):
            if not has_admin_roles:
                no_perms = Embed(
                    title="Error",
                    description="You do not have permissions for this command!",
                    color=self.client.error
                )
                return await ctx.send(embed=no_perms)

        # Send Confirmation Embed
        confirm_embed = Embed(
            title="Add Support",
            description=f"Please confirm that you want to add {user_or_role.mention} to the default support representative team",
            color=self.client.success
        )

        button = Button(
            style=ButtonStyle.PRIMARY,
            label="Confirm",
            custom_id=f"addsupport_{user_or_role.id}",
        )

        await ctx.send(embed=confirm_embed, components=button)


def setup(client: Client):
    AddAdmin(client)