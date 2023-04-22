from interactions import Extension, Client, SlashContext, subcommand, slash_option, OptionType, \
    GuildChannel, Embed

from database.guild import GuildDB


class Transcripts(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @subcommand(
        base="set",
        name="transcripts",
        description="Easily configure the ticket.json transcripts settings",
    )
    @slash_option(
        name="channel",
        description="The channel that ticket.json transcripts should be sent to",
        required=True,
        opt_type=OptionType.CHANNEL
    )
    async def transcripts(self, ctx: SlashContext, channel: GuildChannel):
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

        transcript = {'transcripts.store_transcripts': True, 'transcripts.transcript_channel': channel.id}
        db.update_guild_info(**transcript)

        confirm_embed = Embed(
            title="Setup",
            description=f"The transcripts channel has been changed to {channel.mention}",
            color=self.client.success
        )
        return await ctx.send(embed=confirm_embed)


def setup(client: Client):
    Transcripts(client)