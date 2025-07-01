import discord
import mariadb
import random

from discord.ext import tasks

from dotenv import load_dotenv
import os
load_dotenv()

import matplotlib.pyplot as plt
import random

intents = discord.Intents(messages=True, guilds=True)
intents.members = True
intents.message_content = True
intents.emojis = True
intents.voice_states = True

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

            print("connected successfully to the database")
            print('-------------------------------------')

        except mariadb.Error as e:
            print(f"Couldn't connect to MariaDB server {e}")

bot = Agie(intents=intents)
bot.connection = ""
bot.cursor = ""

@bot.command(description="Mostra latência do bot")
async def ping(ctx):
    await ctx.respond(f"Pong! A latência é: {bot.latency}")

@bot.command(description="Diz um número aleatório entre dois valores")
async def number(ctx, inicial: int, final: int):
    value = random.randint(inicial, final)
    await ctx.respond(f"Seu número aleatório é: {value}")

@bot.command(description="Get all members")
async def get_members(ctx):
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

    # Add to discord_users
    bot.cursor.execute("INSERT IGNORE INTO discord_users (id, global_name) VALUES (?, ?)", (member.id, member.global_name))

    # Add a 1:1 row for user_configs
    bot.cursor.execute("INSERT IGNORE INTO user_configs (user_id) VALUES (?)", (member.id,))

    # Add a 1:1 row for pomodoro_preferences
    bot.cursor.execute("INSERT IGNORE INTO pomodoro_preferences (user_id) VALUES (?)", (member.id,))

    # Add a 1:1 row for timer_visual_preferences
    bot.cursor.execute("INSERT IGNORE INTO timer_visual_preferences (user_id) VALUES(?)", (member.id,))

    bot.connection.commit()

@bot.event
async def on_member_remove(member):

    bot.cursor.execute("DELETE FROM discord_users WHERE discord_users.id = (?)", (member.id,))
    bot.connection.commit()

@bot.command(description="Gera um gráfico pessoal do membro")
async def grafico(ctx):

    user_id = int(ctx.author.id)

    bot.cursor.execute("""
    SET @initial_date = (
        SELECT DATE(focus_datetime) - INTERVAL 1 DAY
        FROM focus_sessions as fs
        WHERE fs.user_id = (?)
        ORDER BY fs.focus_datetime ASC
        LIMIT 1
        );
    """, (user_id,))
                       
    bot.cursor.execute("SET @end_date = DATE(CURDATE());")

    bot.cursor.execute("""
    SET @difference = (
            SELECT DATEDIFF(@end_date, @initial_date) 
        );
    """)
    
    bot.cursor.execute(
    """
    SELECT CONCAT(LPAD(DAY(dt.dates), 2, '0'), '/', LPAD(MONTH(dt.dates), 2, '0')) AS dates,
        COALESCE(fs.minutes/60, 0) AS minutes
            FROM (WITH RECURSIVE number AS (
            SELECT 1 AS num
            UNION ALL
            SELECT num + 1
            FROM number
            WHERE num < @difference
            ) SELECT @initial_date + INTERVAL num DAY AS dates FROM number) AS dt
        LEFT JOIN
            (SELECT 
            CONCAT('<@', user_id, '>') as user_id,
            FLOOR(SUM(fst.duration_minutes)/60) AS hours,
            SUM(fst.duration_minutes)%60 AS minutes,
            fst.focus_datetime
        FROM 
            focus_sessions AS fst
        WHERE
            user_id = (?)
        GROUP BY
            DATE(fst.focus_datetime)) AS fs
        ON
        DATE(fs.focus_datetime) = dt.dates
        ORDER BY
            dt.dates;
    """, (user_id,))

    bot.connection.commit()
    
    content = bot.cursor.fetchall()

    x_values = [data_point[0] for data_point in content]
    y_values = [data_point[1] for data_point in content]

    fig, ax = plt.subplots()
    ax.plot(x_values, y_values, label=f"{ctx.author.global_name}")
    ax.set_xlabel('Dias')
    ax.set_ylabel('Horas')
    ax.set_title(f"Tempo de foco de {ctx.author.global_name}")
    ax.legend()

    plt.savefig("graph.jpeg")

    await ctx.send(file=discord.File('graph.jpeg'))

bot.load_extension('cogs.messages')
bot.load_extension('cogs.moderation')
bot.load_extension('cogs.timers')
bot.run(os.getenv("BOT_TOKEN_DEVELOPING"))