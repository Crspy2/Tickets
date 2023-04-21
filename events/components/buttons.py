from interactions import listen, Client, Extension, Embed, Button, ButtonStyle, EmbedFooter, ActionRow
from interactions.api.events import Component

from database.guild import GuildDB
from database.ticket import TicketDB


class Buttons(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @listen()
    async def on_component(self, event: Component):
        db = GuildDB(event.ctx.guild)
        tickets = TicketDB(event.ctx.guild)
        settings = db.get_guild_info()
        admins = settings.get('admins')
        support = settings.get('support')

        custom_id = event.ctx.custom_id
        if custom_id.startswith("addadmin_"):
            new_admin_id = custom_id.split("_")[1]
            new_admin = event.ctx.guild.get_member(new_admin_id)

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
            if db.is_user_admin(new_admin):
                error_embed = Embed(
                    title="Error",
                    description="User is already an admin!",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=error_embed, components=[])

            # Check if user is a support representative
            if db.is_user_support(new_admin):
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
            new_support = event.ctx.guild.get_member(new_support_id)
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
            if db.is_user_admin(new_support):
                error_embed = Embed(
                    title="Error",
                    description="User is already an admin!",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=error_embed, components=[])

            # Check if user is already on the support team:
            if db.is_user_support(new_support):
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
        elif custom_id.startswith("close"):
            if not settings.get('users_can_close'):
                if not (db.is_user_admin(event.ctx.author) or db.is_user_support(event.ctx.author)):
                    not_allowed = Embed(
                        title="Invalid Permissions",
                        description="You don't have the required permissions to close this ticket!",
                        color=self.bot.error
                    )
                    return await event.ctx.send(embed=not_allowed, ephemeral=True)
            ticket_channel = event.ctx.guild.get_channel(custom_id.split("_")[1])

            await ticket_channel.send("Closed")


        elif custom_id.startswith("close_with_reason"):
            if not settings.get('users_can_close'):
                not_allowed = Embed(
                    title="Invalid Permissions",
                    description="You don't have the required permissions to close this ticket!",
                    color=self.bot.error
                )
                return await event.ctx.send(embed=not_allowed, ephemeral=True)
            ticket_channel = event.ctx.guild.get_channel(custom_id.split("_")[1])

        elif custom_id.startswith("claim"):

            author_roles = []
            for role in event.ctx.author.roles:
                author_roles.append(str(role.id))

            has_admin_roles = set(author_roles).intersection(set(admins))

            # Check if interaction author is an admin
            if not db.is_user_admin(event.ctx.author):
                if not has_admin_roles:
                    no_perms = Embed(
                        title="Error",
                        description="You do not have permissions for this command!",
                        color=self.client.error
                    )
                    return await event.ctx.send(embed=no_perms, ephemeral=True)

            subject = custom_id.split("_")[1]
            ticket_channel = event.ctx.guild.get_channel(custom_id.split("_")[2])
            ticket_message = ticket_channel.get_message(custom_id.split("_")[3])

            tickets.update_ticket_info(ticket_channel, **{'claimed': True}, **{'claimed_by': event.ctx.author.id})
            ticket_embed = Embed(
                title=subject if subject is not None else 'No subject given',
                description=settings.get('welcome_message'),
                color=self.bot.success,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            components = ActionRow(
                Button(
                    style=ButtonStyle.RED,
                    label="Close",
                    emoji="🔒",
                    custom_id=f"close"
                ),
                Button(
                    style=ButtonStyle.RED,
                    label="Close With Reason",
                    emoji="🔒",
                    custom_id=f"close_with_reason"
                )
            )
            await ticket_message.edit(embed=ticket_embed, components=[components])
            await ticket_channel.set_permission(event.ctx.author, view_channel=True)

            claimed = Embed(
                title="Claimed Ticket",
                description=f"Your ticket will be handled by {event.ctx.author.mention}",
                color=self.bot.success,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            admins = []
            for admin in (settings.get('admins') and settings.get('support')):
                a = await self.client.fetch_user(admin)
                if a is not None:
                    admins.append(a)
                a = await event.ctx.guild.fetch_role(admin)
                if a is not None:
                    admins.append(a)

            if not settings.get('claim_settings.support_can_view'):
                for admin in admins:
                    await ticket_channel.set_permission(admin, view_channel=False)

            if not settings.get('claim_settings.support_can_type'):
                for admin in admins:
                    await ticket_channel.set_permission(admin, send_messages=False)

            return await event.ctx.send(embed=claimed)



def setup(client: Client):
    Buttons(client)