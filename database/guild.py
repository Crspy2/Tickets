import os
from typing import Mapping

from pymongo import MongoClient
from interactions import Guild, Snowflake, User, Member, Role
from dotenv import load_dotenv

load_dotenv()


class GuildDB:
    def __init__(self, guild: Guild):
        self.guild = guild
        self.client = MongoClient("MONGO_URL")
        self.db = self.client[f'{guild.id}']
        self.settings = self.db['settings']

    def __del__(self):
        self.client.close()

    def __repr__(self):
        return f"<GuildDB(uri={os.environ.get('DB_URL')}, guild={self.guild})>"

    async def create_guild(self):
        guild_owner = await self.guild.fetch_owner()
        guild_info = {
            "guild_id": self.guild.id,
            "total_tickets": 0,
            "hide_claim_button": False,
            "disable_open_command": False,
            "ticket_notification_channel": None,
            "admins": [guild_owner.user.id],
            "support": [],
            "blacklisted": [],
            "claim_settings": {
                "support_can_view": True,  # Implement: OPEN
                "support_can_type": False  # Implement: OPEN
            },
            "limit": 1,
            "close_confirmation": True,  # Implement: OPEN
            "users_can_close": True,
            "ping_user_on_open": True,
            "ping_admin_on_open": True,
            "feedback_enabled": True,
            "on_call_role": None,  # Implement: OPEN
            "default_category": None,
            "default_naming_schema": "ticket-{{username}}",
            "close_on_leave": True,  # Implement: OPEN
            "welcome_message": "Thank you for contacting support.\nPlease describe your issue (and provide an invite to your server if applicable) and wait for a response.",
            "threads": {
                "use_threads": False,
                "thread_notification_channel": None
            },
            "transcripts": {
                "store_transcripts": False,
                "transcript_channel": None
            },
            "overflow": {
                "overflow_enabled": False,
                "overflow_category": None
            },
            "premium": {
                "is_premium": False,
                "expiry": None
            }
        }

        guild_column = self.settings.insert_one(guild_info)
        return guild_column

    def get_guild_info(self) -> Mapping[str, any] | None:
        guild = self.settings.find_one({"guild_id": self.guild.id})
        return guild

    def update_guild_info(self, **kwargs) -> int:
        result = None
        for key, value in kwargs.items():
            update_query = {"$set": {key: value}}
            result = self.settings.update_one({"guild_id": self.guild.id}, update_query)
        return result.modified_count

    def delete_guild(self) -> int:
        result = self.settings.delete_one({"guild_id": self.guild.id})
        return result.deleted_count

    def is_user_admin(self, user_or_role: Member | Role) -> bool:
        is_admin = user_or_role.id in self.get_guild_info().get('admins', [])
        if not is_admin and type(user_or_role) is not Role:
            for role in user_or_role.roles:
                if role.id in self.get_guild_info().get('admins', []):
                    return True
                else:
                    return False
        return True

    def is_user_support(self, user_or_role: Member | Role) -> bool:
        is_support = user_or_role.id in self.get_guild_info().get('support', [])
        if not is_support and type(user_or_role) is not Role:
            for role in user_or_role.roles:
                if role.id in self.get_guild_info().get('support', []):
                    return True
                else:
                    return False
        return True