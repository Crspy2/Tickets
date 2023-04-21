from interactions import Extension, Client, Embed, SlashContext, slash_command, \
    EmbedFooter, Timestamp, EmbedAttachment
from datetime import datetime


class Invite(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="invite",
        description="Invite the bot to your own server",
    )
    async def invite(self, ctx: SlashContext):
        invite_embed = Embed(
            title="Invite Me To Your Guild",
            description=f"**[Invite Me](https://discord.com/api/oauth2/authorize?client_id=1084995380426588271&permissions=8&scope=bot%20applications.commands) "
                        f"to your server by clicking on the My profile, then clicking on the 'Add to Server' button. "
                        f"\nAlternatively, you can click below to [Invite Me](https://discord.com/api/oauth2/authorize?client_id=1084995380426588271&permissions=8&scope=bot%20applications.commands) "
                        f"to your server!**",
            color=self.client.success,
            footer=EmbedFooter(
                text=f"Requested by {ctx.author.user.username}"
            ),
            url="https://discord.gg/alterasms",
            thumbnail=EmbedAttachment(ctx.author.user.avatar.url),
            timestamp=Timestamp.fromdatetime(datetime.now())
        )

        await ctx.send(embed=invite_embed, ephemeral=True)


def setup(client: Client):
    Invite(client)