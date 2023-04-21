import os
from interactions import Client, Intents, Status, Activity, ActivityType
from handlers import events, commands
from dotenv import load_dotenv
load_dotenv()

# Create bot as an instance of Client()
bot = Client(
    token=os.environ.get('TOKEN'),
    intents=Intents.DEFAULT,
    debug_scope=1088252788271759421,
    owner_ids=[385568884511473664],
    send_command_tracebacks=True,
    show_ratelimit_tracebacks=True,
    delete_unused_application_commands=True,
    basic_logging=True,
)

bot.success = 0x65C97A
bot.error = 0xE85041

# Load Handlers
commands.load(bot)
events.load(bot)

bot.start()
