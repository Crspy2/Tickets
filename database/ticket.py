import os
import time
from typing import Mapping

from pymongo import MongoClient
from interactions import Guild, GuildChannel, User, Snowflake
from dotenv import load_dotenv


load_dotenv()


class TicketDB:
    def __init__(self, guild: Guild):
        self.guild = guild
        self.client = MongoClient("MONGO_URL")
        self.db = self.client[f'{self.guild.id}']
        self.tickets = self.db['tickets']
        self.settings = self.db['settings']

    def __del__(self):
        self.client.close()

    def __repr__(self):
        return f"<TicketDB(uri={os.environ.get('DB_URL')}, guild={self.guild})>"

    def create_ticket(self, channel: GuildChannel, user: User, panel_id: int = 0):
        self.settings.update_one({}, {'$inc': {'total_tickets': 1}})
        ticket_info = {
            "guild_id": self.guild.id,
            "ticket_id": self.settings.find_one({"guild_id": self.guild.id}).get('total_tickets'),
            "channel_id": channel.id,
            "panel_id": panel_id,
            "user_id": user.id,
            "close_at": None,
            "close_reason": None,
            "claimed": False,
            "claimed_by": None,
            "opened_at": time.time(),
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

    def delete_ticket(self, ticket_channel: GuildChannel) -> int:
        result = self.tickets.delete_one({"channel_id": ticket_channel.id})
        return result.deleted_count

    def user_tickets(self, user: User) -> int:
        count = self.tickets.count_documents({'user_id': user.id})
        return count
