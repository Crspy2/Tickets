import time

from interactions import listen, Client, Extension, Embed, Button, ButtonStyle, EmbedFooter, ActionRow, Modal, \
    ModalContext, ParagraphText, EmbedAuthor, EmbedField
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
            if new_admin is None:
                new_admin = event.ctx.guild.get_role(new_admin_id)

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
            print(f"Person's admin status is {db.is_support(new_admin.id)}")
            if db.is_admin(new_admin.id) is True:
                error_embed = Embed(
                    title="Error",
                    description="User is already an admin!",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=error_embed, components=[])

            # Check if user is a support representative
            if db.is_support(new_admin.id):
                support = support
                support.remove(new_admin_id)

            admins.append(new_admin.id)

            db.update_guild_info(**{'admins': admins}, **{'support': support})

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
            if new_support is None:
                new_support = event.ctx.guild.get_role(new_support_id)
            # Check if user is OWNER
            owner = await event.ctx.guild.fetch_owner()
            if new_support.id == owner.id:
                is_owner = Embed(
                    title="Error",
                    description="The server owner is already an administrator",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=is_owner, components=[])

            # Check if user is already a support rep:
            if db.is_admin(new_support.id) is True:
                error_embed = Embed(
                    title="Error",
                    description="User is already an admin!",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=error_embed, components=[])

            # Check if user is already on the support team:
            if db.is_support(new_support.id):
                error_embed = Embed(
                    title="Error",
                    description="User is already a support representative!",
                    color=self.client.error
                )
                return await event.ctx.edit_origin(embed=error_embed, components=[])

            support.append(new_support.id)
            support = {'support': support}

            db.update_guild_info(**support)

            # Tell user how it went!
            confirm_embed = Embed(
                title="Add Support",
                description=f"Support representative added successfully",
                color=self.client.success
            )
            return await event.ctx.edit_origin(embed=confirm_embed, components=[])
        elif custom_id == "close-with-reason":
            if not settings.get('users_can_close'):
                not_allowed = Embed(
                    title="Invalid Permissions",
                    description="You don't have the required permissions to close this ticket!",
                    color=self.bot.error
                )
                return await event.ctx.channel.send(embed=not_allowed, ephemeral=True)

            reason = Modal(
                ParagraphText(
                    label="Reason",
                    placeholder='Reason for closing the ticket, e.g. "Resolved"',
                    custom_id="reason"
                ),
                title="My Modal",
            )
            await event.ctx.send_modal(modal=reason)

            modal_ctx: ModalContext = await event.ctx.bot.wait_for_modal(reason)
            await tickets.close_ticket(modal_ctx)
        elif custom_id == "close":
            if not settings.get('users_can_close'):
                if not (db.is_admin(event.ctx.author.id) or db.is_support(event.ctx.author.id)):
                    not_allowed = Embed(
                        title="Invalid Permissions",
                        description="You don't have the required permissions to close this ticket!",
                        color=self.bot.error
                    )
                    return await event.ctx.send(embed=not_allowed, ephemeral=True)
            await tickets.close_ticket(event.ctx)
        elif custom_id.startswith("claim"):

            author_roles = []
            for role in event.ctx.author.roles:
                author_roles.append(str(role.id))

            has_admin_roles = set(author_roles).intersection(set(admins))

            # Check if interaction author is an admin
            if not db.is_admin(event.ctx.author.id):
                if not has_admin_roles:
                    no_perms = Embed(
                        title="Error",
                        description="You do not have permissions for this command!",
                        color=self.client.error
                    )
                    return await event.ctx.send(embed=no_perms, ephemeral=True)

            subject = custom_id.split("_")[1]
            ticket_channel = event.ctx.channel
            ticket_message = event.ctx.message
            # ticket_channel = event.ctx.guild.get_channel(custom_id.split("_")[2])
            # ticket_message = ticket_channel.get_message(custom_id.split("_")[3])

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
                    custom_id=f"close-with-reason"
                )
            )
            await ticket_message.edit(embed=ticket_embed, components=[components])

            claimed = Embed(
                title="Claimed Ticket",
                description=f"Your ticket will be handled by {event.ctx.author.mention}",
                color=self.bot.success,
                footer=EmbedFooter(
                    text="Powered by altera.vip",
                    icon_url=self.bot.user.avatar.url
                )
            )
            support = []
            for rep in settings.get('support'):
                a = await self.client.fetch_user(rep)
                if a is not None:
                    support.append(a)
                a = await event.ctx.guild.fetch_role(rep)
                if a is not None:
                    support.append(a)
            if not settings.get('claim_settings.support_can_view'):
                for rep in support:
                    await ticket_channel.set_permission(rep, view_channel=False)
            elif not settings.get('claim_settings.support_can_type'):
                for rep in support:
                    await ticket_channel.set_permission(rep, view_channel=True, send_messages=False, add_reactions=False)

            return await event.ctx.send(embed=claimed)



def setup(client: Client):
    Buttons(client)
