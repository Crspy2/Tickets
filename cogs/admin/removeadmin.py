from interactions import Extension, Client, SlashContext, OptionType, User, Role, Embed, \
    slash_command, slash_option

from database.guild import GuildDB


class RemoveAdmin(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="removeadmin",
        description="Revokes a user's or role's admin privileges"
    )
    @slash_option(
        name="user_or_role",
        description="User or role to remove the administrator permissions from",
        required=True,
        opt_type=OptionType.MENTIONABLE
    )
    async def removeadmin(self, ctx: SlashContext, user_or_role: User | Role):
        await ctx.defer(ephemeral=True)
        db = GuildDB(ctx.guild)
        settings = db.get_guild_info()
        admins = settings['admins']

        author_roles = []
        for role in ctx.author.roles:
            author_roles.append(str(role.id))

        has_admin_roles = set(author_roles).intersection(set(admins))

        # Check if interaction author is not an admin
        if not db.is_user_admin(ctx.author):
            if not has_admin_roles:
                no_perms = Embed(
                    title="Error",
                    description="You do not have permissions for this command!",
                    color=self.client.error
                )
                return await ctx.send(embed=no_perms)

        owner = await ctx.guild.fetch_owner()
        print(f"The Server Owner is: {owner}")
        if user_or_role.id == owner.id:
            is_owner = Embed(
                title="Error",
                description="The server owner must be an admin",
                color=self.client.error
            )
            return await ctx.send(embed=is_owner)

        # Check if user is already an admin:
        if not db.is_user_admin(user_or_role):
            error_embed = Embed(
                title="Error",
                description="User is not an admin!",
                color=self.client.error
            )
            return await ctx.send(embed=error_embed)

        admins.remove(str(user_or_role.id))
        admins = {'admins': admins}

        db.update_guild_info(admins=admins)

        # Send Confirmation Embed
        confirm_embed = Embed(
            title="Remove Admin",
            description=f"Admin removed successfully",
            color=self.client.success,
        )

        await ctx.send(embed=confirm_embed)


def setup(client: Client):
    RemoveAdmin(client)