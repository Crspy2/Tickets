from interactions import Extension, Client, SlashContext, slash_command, EmbedField, Embed

from database.guild import GuildDB


class ViewStaff(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="viewstaff",
        description="Lists the staff members and roles",
    )
    async def viewstaff(self, ctx: SlashContext):
        await ctx.defer(ephemeral=True)
        db = GuildDB(ctx.guild)
        settings = db.get_guild_info()
        admins = settings.get('admins')
        support_reps = settings.get('support')

        admin_roles = []
        admin_users = []
        support_roles = []
        support_users = []

        for admin in admins:
            a = self.client.get_user(admin)
            if a is not None:
                admin_users.append(a)

            a = ctx.guild.get_role(admin)
            if a is not None:
                admin_roles.append(a)

        for support in support_reps:
            s = self.client.get_user(support)
            if s is not None:
                support_users.append(s)

            s = ctx.guild.get_role(support)
            if s is not None:
                support_roles.append(s)

        e = Embed(
            title="Staff",
            color=self.client.success,
            fields=[
                EmbedField(
                    name="Admin Users",
                    value=f"\n".join([f"• {user.mention} (`{user.id}`)" for user in admin_users]) if admin_users else "No admin users",
                    inline=True
                ),
                EmbedField(
                    name="Admin Roles",
                    value=f"\n".join([f"• {user.mention} (`{user.id}`)" for user in admin_roles]) if admin_roles else "No admin roles",
                    inline=True
                ),
                EmbedField(
                    name="\u200b",
                    value="\u200b",
                    inline=False
                ),
                EmbedField(
                    name="Support Representatives",
                    value=f"\n".join([f"• {user.mention} (`{user.id}`)" for user in support_users]) if support_users else "No support representatives",
                    inline=True
                ),
                EmbedField(
                    name="Support Roles",
                    value=f"\n".join([f"• {user.mention} (`{user.id}`)" for user in support_roles]) if support_roles else "No support roles",
                    inline=True
                )
            ]
        )


        await ctx.send(embed=e)


def setup(client: Client):
    ViewStaff(client)