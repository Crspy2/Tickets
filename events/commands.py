import sys

from interactions import listen, Client, Extension, Embed
from interactions.client import errors
from interactions.api import events
import traceback


class CommandEvents(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client


    @listen(disable_default_listeners=True)
    async def on_command_error(self, event: events.CommandError):
        ctx = event.ctx
        log_channel = await ctx.guild.fetch_channel(self.bot.log_channel_id)
        if type(event.error) is errors.CommandOnCooldown:
            cooldown_time = await ctx.command.cooldown.get_cooldown_time(event.ctx)
            cooldown = Embed(
                title="You are on cooldown!",
                description=f"Please try again in **{cooldown_time:.0f}** seconds",
                color=event.bot.error
            )
            # THIS ISN'T AN ERROR, DONT CHANGE
            return await ctx.send(embed=cooldown, ephemeral=True)
        if type(event.error) is KeyError:
            error = Embed(
                title="Response Error",
                description="Something went wrong while indexing your response! If this error persists, please contact support and refrain from re-executing the command!",
                color=self.bot.error
            )
            await ctx.send(embed=error, ephemeral=True)

            log_e = Embed(
                title="Key error",
                description=f"```bash\n{event.error.with_traceback(sys.exc_info()[2])}\n```"
            )

            return await log_channel.send("<@385568884511473664>", embed=log_e)
        else:
            error = Embed(
                title="An Error Occurred",
                description="Something went wrong while you ran this command. If this error persists, please contact support and refrain from re-executing the command!",
                color=self.bot.error
            )
            await ctx.send(embed=error, ephemeral=True)

            tb_list = traceback.format_exception(type(event.error), event.error, event.error.__traceback__)
            tb_str = ''.join(tb_list)
            print(tb_str)
            log_e = Embed(
                title="Error",
                description=f"```{tb_str}```",
                color=self.bot.error
            )

            return await log_channel.send("<@385568884511473664>", embed=log_e)


def setup(client: Client):
    CommandEvents(client)