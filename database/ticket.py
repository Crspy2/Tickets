import os
import time
from typing import Mapping

from pymongo import MongoClient
from interactions import Guild, GuildChannel, User, ModalContext, Embed, EmbedAuthor, EmbedField, Timestamp, \
    ComponentContext
from dotenv import load_dotenv


load_dotenv()


class TicketDB:
    def __init__(self, guild: Guild):
        self.guild = guild
        self.client = MongoClient("mongodb://mongo:muDE7My0G7Db02HHxo2I@containers.railway.app:5473")
        self.db = self.client[f'{self.guild.id}']
        self.tickets = self.db['tickets']
        self.settings = self.db['settings']

    def __del__(self):
        self.client.close()

    def __repr__(self):
        return f"<TicketDB(guild={self.guild})>"

    def create_ticket(self, channel: GuildChannel, user: User, panel_id: int = 0):
        self.settings.update_one({}, {'$inc': {'total_tickets': 1}})
        ticket_info = {
            "guild_id": self.guild.id,
            "ticket_id": self.settings.find_one({"guild_id": self.guild.id}).get('total_tickets'),
            "channel_id": channel.id,
            "panel_id": panel_id,
            "user_id": user.id,
            "closed_at": None,
            "close_reason": None,
            "claimed": False,
            "claimed_by": None,
            "opened_at": int(time.time()),
            "response_time": None,
            "last_message_id": None,
            "last_message_time": None
        }
        ticket_column = self.tickets.insert_one(ticket_info)
        return ticket_column

    def get_ticket_info(self, ticket_channel: GuildChannel) -> Mapping[str, any] | None:
        guild = self.tickets.find_one({"channel_id": ticket_channel.id})
        return guild

    def update_ticket_info(self, ticket_channel: GuildChannel, **kwargs) -> int:
        result = None
        for key, value in kwargs.items():
            update_query = {"$set": {key: value}}
            result = self.tickets.update_one({"channel_id": ticket_channel.id}, update_query)
        return result.modified_count

    async def close_ticket(self, ctx: ModalContext | ComponentContext) -> None:
        update = {
            "$set": {
                "close_reason": 'No reason specified' if ctx.responses is None else ctx.responses.get('reason'),
                "closed_at": int(time.time()),
            }
        }
        self.tickets.update_one({"channel_id": ctx.channel.id}, update)

        this_ticket = self.get_ticket_info(ctx.channel)
        transcript = Embed(
            author=EmbedAuthor(
                name=ctx.guild.name,
                icon_url="https://imgur.com/qqwX4Nx" if ctx.guild.icon is None else ctx.guild.icon.url
            ),
            title="Ticket Closed",
            fields=[
                EmbedField(name="Ticket ID", value=f"{this_ticket.get('ticket_id')}", inline=True),
                EmbedField(name="Opened By", value=f"<@{this_ticket.get('user_id')}>", inline=True),
                EmbedField(name="Closed By", value=ctx.author.mention, inline=True),
                EmbedField(name="Open Time", value=f"<t:{this_ticket.get('opened_at')}>", inline=True),
                EmbedField(name="Claimed By", value='Not Claimed' if this_ticket.get(
                    'claimed_by') is None else f"<@{this_ticket.get('claimed_by')}>", inline=True),
                EmbedField(name="Reason", value=this_ticket.get('close_reason'), inline=True),
            ],
            timestamp=Timestamp.utcnow()
        )
        self.tickets.delete_one({"channel_id": ctx.channel.id})
        await ctx.channel.delete(f"Ticket was closed by {ctx.author.user.username}#{ctx.author.user.discriminator}")
        await ctx.author.send(embed=transcript)


    def delete_ticket(self, ticket_channel: GuildChannel) -> int:
        result = self.tickets.delete_one({"channel_id": ticket_channel.id})
        return result.deleted_count

    def user_tickets(self, user: User) -> int:
        count = self.tickets.count_documents({'user_id': user.id})
        return count
