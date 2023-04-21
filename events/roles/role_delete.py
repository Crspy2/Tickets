from interactions import listen, Client, Extension
from interactions.api.events import RoleDelete

from database.guild import GuildDB


class OnRoleDelete(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @listen()
    async def on_role_delete(self, event: RoleDelete):
        db = GuildDB(event.guild)
        settings = db.get_guild_info()
        admins = settings['admins']
        support = settings['support']

        if db.is_user_admin(event.role.id):
            admins.remove(event.role.id)
            new_admins = {'admins': admins}

            db.update_guild_info(**new_admins)

        elif db.is_user_support(event.role.id):
            support.remove(event.role.id)
            new_support = {'support': support}

            db.update_guild_info(**new_support)


        else:
            pass

def setup(client: Client):
    OnRoleDelete(client)