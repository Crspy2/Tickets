from interactions import Extension, Client, SlashContext, Embed, slash_command, slash_option, OptionType, EmbedFooter, \
    Button, ButtonStyle, ActionRow

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
        guild_info = guild_db.get_guild_info()
        if guild_info.get('disable_open_command'):
            open_disabled = Embed(
                title="Command Disabled",
                description="The `/open` command has been disabled on this server.",
                color=self.bot.error
            )
            return await ctx.send(embed=open_disabled, ephemeral=True)

        if ctx.author.user.id in guild_info.get('blacklisted'):
            blacklisted = Embed(
                title="Blacklisted User",
                description="You have been blacklisted from our ticket service!",
                color=self.bot.error
            )
            return await ctx.send(embed=blacklisted, ephemeral=True)

        if tickets_db.user_tickets(ctx.author) >= guild_info.get('limit'):
            ticket_limit = Embed(
                title="Ticket Limit Reached",
                description="You already have the maximum amount of allowed tickets open at once!",
                color=self.bot.error
            )
            return await ctx.send(embed=ticket_limit, ephemeral=True)

        guild_naming_scheme = guild_info.get('default_naming_schema')
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
                guild_naming_scheme.replace(f"{{{var}}}", (guild_info.get('total_tickets') + 1))

        ticket_channel = await ctx.guild.create_text_channel(
            name=guild_naming_scheme,
            topic=subject,
            category=guild_info.get('default_category'),
            reason=f"{ctx.author.user}#{ctx.author.discriminator} opened a support ticket via the `/open` command!"
        )
        admins = []
        for admin in (guild_info.get('admins') and guild_info.get('support')):
            a = await self.client.fetch_user(admin)
            if a is not None:
                admins.append(a)
            a = await ctx.guild.fetch_role(admin)
            if a is not None:
                admins.append(a)

        open_embed = Embed(
            title="Ticket",
            description=f"Opened a new ticket: {ticket_channel.mention}",
            color=self.bot.success,
            footer=EmbedFooter(
                text="Powered by altera.vip",
                icon_url=self.bot.user.avatar.url
            )
        )

        await ctx.send(embed=open_embed, ephemeral=True)

        ticket_embed = Embed(
            title=subject if subject is not None else 'No subject given',
            description=guild_info.get('welcome_message'),
            color=self.bot.success,
            footer=EmbedFooter(
                text="Powered by altera.vip",
                icon_url=self.bot.user.avatar.url
            )
        )

        pings = ""
        if guild_info.get('ping_on_open'):  # Ping author and staff
            pings += f"{ctx.author.mention}"
        for item in (guild_info.get('admins') or guild_info.get('support')):
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

        if not guild_info.get('hide_claim_button'):
            components.add_component(
                Button(
                    style=ButtonStyle.GREEN,
                    label="Claim",
                    emoji="🙋‍♂️",
                    custom_id=f"claim_{subject}_{ticket_channel.id}_{ticket_msg.id}"
                )
            )

        await ticket_msg.edit(content="", embed=ticket_embed, components=components)

        return tickets_db.create_ticket(ticket_channel, ctx.author)



def setup(client: Client):
    Open(client)
