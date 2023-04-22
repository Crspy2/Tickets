from interactions import Extension, Client, SlashContext, OptionType, User, Embed, slash_command, slash_option, \
    EmbedFooter

from database.ticket import TicketDB


class UnClaim(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @slash_command(
        name="unclaim",
        description="Removes the claim on the current ticket"
    )
    async def un_claim(self, ctx: SlashContext):
        ...


def setup(client: Client):
    UnClaim(client)
