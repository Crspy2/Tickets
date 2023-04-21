from interactions import listen, Client, Extension


class OnReady(Extension):
    def __init__(self, client: Client):
        self.bot: Client = client

    @listen()
    async def on_ready(self):
        print(f"Logged in as {self.bot.user} (ID: {self.bot.user.id})")


def setup(client: Client):
    OnReady(client)