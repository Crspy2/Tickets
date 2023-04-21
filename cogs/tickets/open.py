from interactions import Extension, Client, SlashContext, Embed, slash_command, slash_option, OptionType, EmbedFooter, \
    Button, ButtonStyle, ActionRow, PermissionOverwrite, Permissions, OverwriteType

from database.guild import GuildDB
from database.ticket import TicketDB


class Open(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="open",
        description="Open a new ticket"
    )
    @slash_option(
        name="subject",
        description="The subject of the ticket",
        required=False,
        opt_type=OptionType.STRING
    )
    async def open(self, ctx: SlashContext, subject: str = None):
        guild_db = GuildDB(ctx.guild)
        tickets_db = TicketDB(ctx.guild)
        settings = guild_db.get_guild_info()
        if settings.get('disable_open_command'):
            open_disabled = Embed(
                title="Command Disabled",
                description="The `/open` command has been disabled on this server.",
                color=self.bot.error
            )
            return await ctx.send(embed=open_disabled, ephemeral=True)

        if ctx.author.user.id in settings.get('blacklisted'):
            blacklisted = Embed(
                title="Blacklisted User",
                description="You have been blacklisted from our ticket service!",
                color=self.bot.error
            )
            return await ctx.send(embed=blacklisted, ephemeral=True)

        if tickets_db.user_tickets(ctx.author) >= settings.get('limit'):
            ticket_limit = Embed(
                title="Ticket Limit Reached",
                description="You already have the maximum amount of allowed tickets open at once!",
                color=self.bot.error
            )
            return await ctx.send(embed=ticket_limit, ephemeral=True)

        guild_naming_scheme = settings.get('default_naming_schema')
        if tickets_db.user_tickets(ctx.author) != 0:
            guild_naming_scheme += f"-{tickets_db.user_tickets(ctx.author)}"
        variables = guild_naming_scheme.split("{{")
        variables = [s.split("}}")[0] for s in variables[1:]]
        for var in variables:
            if var == "username":
                guild_naming_scheme = guild_naming_scheme.replace(f"{{{var}}}", f"{ctx.author.user.username}")
            elif var == "user":
                guild_naming_scheme.replace(f"{{{var}}}", f"{ctx.author.user.username}#{ctx.author.user.discriminator}")
            elif var == "nickname":
                guild_naming_scheme.replace(f"{{{var}}}", f"{ctx.author.display_name}")

            elif var == "tag" or var == "discriminator":
                guild_naming_scheme.replace(f"{{{var}}}", f"{ctx.author.user.discriminator}")
            elif var == "id" or var == "number" or var == "ticket":
                guild_naming_scheme.replace(f"{{{var}}}", (settings.get('total_tickets') + 1))

        ticket_channel = await ctx.guild.create_text_channel(
            name=guild_naming_scheme,
            topic=subject,
            category=settings.get('default_category'),
            reason=f"{ctx.author.user}#{ctx.author.discriminator} opened a support ticket via the `/open` command!"
        )
        await ticket_channel.edit_permission(PermissionOverwrite(
            type=OverwriteType.ROLE,
            id=ctx.guild.default_role.id,
            deny=Permissions.VIEW_CHANNEL
        ))
        await ticket_channel.set_permission(ctx.author, add_reactions=True, attach_files=True,
                                            read_message_history=True, send_messages=True,
                                            use_application_commands=True, use_external_emojis=True,
                                            use_external_stickers=True, view_channel=True)

        admins = []
        for admin in (settings.get('admins') and settings.get('support')):
            a = await self.client.fetch_user(admin)
            if a is not None:
                admins.append(a)
            a = await ctx.guild.fetch_role(admin)
            if a is not None:
                admins.append(a)

        for admin in admins:
            await ticket_channel.set_permission(admin, add_reactions=True, attach_files=True,
                                                read_message_history=True, send_messages=True,
                                                use_application_commands=True, use_external_emojis=True,
                                                use_external_stickers=True, view_channel=True)

        ticket_embed = Embed(
            title=subject if subject is not None else 'No subject given',
            description=settings.get('welcome_message'),
            color=self.bot.success,
            footer=EmbedFooter(
                text="Powered by altera.vip",
                icon_url=self.bot.user.avatar.url
            )
        )

        pings = ""
        if settings.get('ping_on_open'):  # Ping author and staff
            pings += f"{ctx.author.mention}"
        if settings.get('ping_admin_on_open'):
            for item in (settings.get('admins') or settings.get('support')):
                pings += f"<@{item}>"
        ticket_msg = await ticket_channel.send(content=pings, embed=ticket_embed)

        components = ActionRow(
            Button(
                style=ButtonStyle.RED,
                label="Close",
                emoji="🔒",
                custom_id=f"close_{ticket_channel.id}"
            ),
            Button(
                style=ButtonStyle.RED,
                label="Close With Reason",
                emoji="🔒",
                custom_id=f"close_with_reason_{ticket_channel.id}"
            )
        )

        if not settings.get('hide_claim_button'):
            components.add_component(
                Button(
                    style=ButtonStyle.GREEN,
                    label="Claim",
                    emoji="🙋‍♂️",
                    custom_id=f"claim_{subject}_{ticket_channel.id}_{ticket_msg.id}"
                )
            )

        await ticket_msg.edit(content="", embed=ticket_embed, components=components)

        tickets_db.create_ticket(ticket_channel, ctx.author)

        open_embed = Embed(
            title="Ticket",
            description=f"Opened a new ticket: {ticket_channel.mention}",
            color=self.bot.success,
            footer=EmbedFooter(
                text="Powered by altera.vip",
                icon_url=self.bot.user.avatar.url
            )
        )

        return await ctx.send(embed=open_embed, ephemeral=True)



def setup(client: Client):
    Open(client)
