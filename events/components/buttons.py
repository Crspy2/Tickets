from interactions import listen, Client, Extension, Embed
from interactions.api.events import Component

from database.guild import GuildDB


class Buttons(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @listen()
    async def on_component(self, event: Component):
        db = GuildDB(event.ctx.guild)
        settings = db.get_guild_info()
        admins = settings.get('admins')
        support = settings.get('support')

        custom_id = event.ctx.custom_id
        if custom_id.startswith("addadmin_"):
            new_admin_id = custom_id.split("_")[1]
            new_admin = event.bot.get_user(new_admin_id)

            # Check if user is OWNER
            owner = await event.ctx.guild.fetch_owner()
            if new_admin.id == owner.id:
                is_owner = Embed(
                    title="Error",
                    description="The server owner must be an admin",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=is_owner, components=[])

            # Check if user is already an admin:
            if db.is_user_admin(new_admin.id):
                error_embed = Embed(
                    title="Error",
                    description="User is already an admin!",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=error_embed, components=[])

            # Check if user is a support representative
            if db.is_user_support(new_admin.id):
                support = support
                support.remove(str(new_admin_id))
                support = {'support': support}

            admins.append(new_admin_id)
            admins = {'admins': admins}

            db.update_guild_info(**admins, **support)

            # Tell user how it went!
            confirm_embed = Embed(
                title="Add Admin",
                description=f"Admin added successfully",
                color=self.client.success
            )
            return await event.ctx.edit_origin(embed=confirm_embed, components=[])
        elif custom_id.startswith("addsupport_"):
            new_support_id = custom_id.split("_")[1]
            new_support = event.bot.get_user(new_support_id)
            # Check if user is OWNER
            owner = await event.ctx.guild.fetch_owner()
            if new_support.id == owner.id:
                is_owner = Embed(
                    title="Error",
                    description="The server owner is already an administrator",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=is_owner, components=[])

            # Check if user is already an admin:
            if db.is_user_admin(new_support.id):
                error_embed = Embed(
                    title="Error",
                    description="User is already an admin!",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=error_embed, components=[])

            # Check if user is already on the support team:
            if db.is_user_support(new_support.id):
                error_embed = Embed(
                    title="Error",
                    description="User is already a support representative!",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=error_embed, components=[])

            support.append(new_support_id)
            support = {'support': support}

            db.update_guild_info(**support)

            # Tell user how it went!
            confirm_embed = Embed(
                title="Add Support",
                description=f"Support representative added successfully",
                color=self.client.success
            )
            return await event.ctx.edit_origin(embed=confirm_embed, components=[])


def setup(client: Client):
    Buttons(client)