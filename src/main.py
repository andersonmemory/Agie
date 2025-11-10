"""Main file for starting the Bot along with its class definition."""

import discord
import mariadb
import random
import asyncio

from dotenv import load_dotenv
import os
load_dotenv()

import random

intents = discord.Intents(messages=True, guilds=True)
intents.members = True
intents.message_content = True
intents.emojis = True
intents.voice_states = True

intents.reactions = True
intents.dm_messages = True


class Agie(discord.Bot): # subclass discord.Bot
    async def on_ready(self): # override the on_ready event
        print('Logged in as ', end="")
        print(self.user.name)
        # print(self.user.id)
        print('------')
        await self.sync_commands()

        try:

            self.connection = mariadb.connect(
                user=os.getenv("DB_USER"),
                password=os.getenv("PASSWORD"),
                host=os.getenv("HOST"),
                database=os.getenv("DATABASE")
            )

            self.cursor = self.connection.cursor()

            asyncio.create_task(keep_db_alive)

            print("connected successfully to the database")
            print('-------------------------------------')

        except mariadb.Error as e:
            print(f"Couldn't connect to MariaDB server {e}")


bot = Agie(intents=intents)
bot.connection = ""
bot.cursor = ""


async def keep_db_alive():
    """ Prevents termination of database connections after 8 hours of inactivity. """
    while True:
        bot.cursor.execute(
        """
            SELECT 1;
        """)
        await asyncio.sleep(60 * 60 * 4)

@bot.command(description="Mostra latência do bot")
async def ping(ctx):
    await ctx.respond(f"Pong! A latência é: {bot.latency}")

@bot.command(description="Diz um número aleatório entre dois valores")
async def number(ctx, inicial: int, final: int):
    value = random.randint(inicial, final)
    await ctx.respond(f"Seu número aleatório é: {value}")

@bot.command(description="Get all members")
async def get_members(ctx):
    """Insert all Discord users in the current server
    in the database, along with their own associated tables.

    Args:
        ctx (discord.ApplicationContext): The context where the feedback message is going to be sent.
    """
    for member in bot.get_all_members():
    
        if not member.bot:

            try:
                # Add to discord_users
                bot.cursor.execute("INSERT IGNORE INTO discord_users (id, global_name) VALUES (?, ?)", (member.id, member.global_name))

                # Add a 1:1 row for user_configs
                bot.cursor.execute("INSERT IGNORE INTO user_configs (user_id) VALUES (?)", (member.id,))

                # Add a 1:1 row for pomodoro_preferences
                bot.cursor.execute("INSERT IGNORE INTO pomodoro_preferences (user_id) VALUES (?)", (member.id,))

                # Add a 1:1 row for timer_visual_preferences
                bot.cursor.execute("INSERT IGNORE INTO timer_visual_preferences (user_id) VALUES(?)", (member.id,))

            except mariadb.Error as e:
                print(f"One error found. Error: {e}")

    await ctx.respond(content="Todos usuários do servidor foram adicionados na database!", ephemeral=True)

    bot.connection.commit()

@bot.event
async def on_member_join(member):
    """Insert a new recently joined user in the current server
    to the database, along with their own associated tables.

    Args:
        member (discord.Member): The Discord member that joined the server.
    """
    try: 
        # Add to discord_users
        bot.cursor.execute("INSERT IGNORE INTO discord_users (id, global_name) VALUES (?, ?)", (member.id, member.global_name))

        # Add a 1:1 row for user_configs
        bot.cursor.execute("INSERT IGNORE INTO user_configs (user_id) VALUES (?)", (member.id,))

        # Add a 1:1 row for pomodoro_preferences
        bot.cursor.execute("INSERT IGNORE INTO pomodoro_preferences (user_id) VALUES (?)", (member.id,))

        # Add a 1:1 row for timer_visual_preferences
        bot.cursor.execute("INSERT IGNORE INTO timer_visual_preferences (user_id) VALUES(?)", (member.id,))

        bot.connection.commit()
    except mariadb.Error as e:
        print(f"MariaDB server error: {e}")

@bot.event
async def on_member_remove(member):
    """Remove a user that left the current server
    from the database, along with their own associated tables.

    Args:
        member (discord.Member): The Discord member that left the server.
    """
    try:

        bot.cursor.execute("DELETE FROM discord_users WHERE discord_users.id = (?)", (member.id,))
        bot.connection.commit()

    except mariadb.Error as e:
        print(f"MariaDB server error: {e}")

bot.load_extension('cogs.messages')
bot.load_extension('cogs.moderation')
bot.load_extension('cogs.timers')
bot.load_extension('cogs.focus_graphs')
bot.run(os.getenv("BOT_TOKEN"))