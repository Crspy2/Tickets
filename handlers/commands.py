import os

from interactions import Client


def load(client: Client):
    handlers_dir = os.path.dirname(os.path.abspath(__file__))
    cogs_dir = os.path.join(os.path.dirname(handlers_dir), 'cogs')

    cogs = []
    for root, dirs, files in os.walk(cogs_dir):
        dirs[:] = [d for d in dirs if d != '__pycache__']
        for module in files:
            if module not in ("__init__.py", "template.py") and module[-3:] == ".py":
                module_path = os.path.join(root, module)
                module_name = module_path[len(os.path.dirname(cogs_dir)) + 1:-3].replace("/", ".")
                cogs.append(module_name)

    for cog in cogs:
        try:
            client.load_extension(cog.replace('\\', '.'))
            print(f"\033[1;92mLoaded the {cog[5:].title().replace('.', '-')} command\033[0m")
        except Exception as err:
            print(f"\033[1;31mFailed to load the {cog[5:].title().replace('.', '-')} command!\n\033[0mFor more info look here: {err}")
    print("\n")
