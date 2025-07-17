# Contains a stopwatch and a pomodoro timer for Agie and related functionalities

import discord
from discord.ext import commands, tasks
import time
import datetime
import random

import asyncio

from utils import helpers_rankings, helpers_timers
from config.settings import (
    SEND_VERIFY_MESSAGE_THRESHOLD,
    WAIT_TO_VERIFY_THRESHOLD,

    POMODORO_CHANNEL_ID,
    STOPWATCH_CHANNEL_ID,
    FOCUS_MESSAGES_CHANNEL_ID,
    AFK_CHANNEL_ID
)

voice_channel_members = []

emojis = [
    "<a:Lit_3:1254122861505810492>", "<a:okayu_dance:1254124509880123513>", "<a:ayame_closer:1254123431692075050>",
    "<a:brown_jump:1254094670565347388>", "<a:dance_Furry_rainbow:1254120564533235823>", "<a:sonicdance:1253660175508967464>",
    "<a:danceboy:1254075410468044833>", "<a:danceChika:1254100280773972082>", "<a:MenheraHappyWave:1384288301774540810>",
    "<a:finger_twirl:1254072415512821862>", "<a:finger_twirl2:1254127339806261268>", "<a:dance_uwu:1254119935739953213>",
    "<a:danceSpin:1254106387487916113>", "<a:pageflip:1254124419995926654>",  "<a:ExcitedHeart:1254107270246170765>",
    "<a:catJAM:1254122448719319122>",
    ]

ranking_values = []

colors = {
    "vermelho":discord.Colour.red(),
    "laranja":discord.Colour.orange(),
    "amarelo":discord.Colour.yellow(),
    "verde":discord.Colour.green(),
    "azul":discord.Colour.blue(),
    "roxo":discord.Colour.purple(),
    "rosa":discord.Colour.nitro_pink(),
    "cinza":discord.Colour.light_grey(),
    "preto":discord.Colour.dark_theme(),
    "aleatório":discord.Colour.random()
}

class Timers(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):

        if member.bot:
            return
        
        # If what changed was just the voice status inside the channel
        try:
            if before.self_deaf != after.self_deaf or before.self_mute != after.self_mute:
                return
        except:
            pass

        self.connection = self.bot.connection
        self.cursor = self.bot.cursor

        bot_connection = self.connection
        bot_cursor = self.cursor

        focus_channel = self.bot.get_channel(FOCUS_MESSAGES_CHANNEL_ID)
        pomodoro_channel = self.bot.get_channel(POMODORO_CHANNEL_ID)
        stopwatch_channel = self.bot.get_channel(STOPWATCH_CHANNEL_ID)
        afk_channel = self.bot.get_channel(AFK_CHANNEL_ID)

        time_voice_channels = [pomodoro_channel, stopwatch_channel]

        on_pomodoro_channel = after.channel == pomodoro_channel

        # Leaving the VC
        if before.channel in time_voice_channels:
            await remove(bot_cursor, bot_connection, member, focus_channel)

        # Joining the VC
        if after.channel in time_voice_channels:
            register(bot_cursor, bot_connection, member, on_pomodoro_channel, focus_channel, afk_channel, self.bot)


    @discord.slash_command(description="altera configurações do pomodoro")
    async def pomodoro(self, ctx):

        # check first if user is in voice call before doing it
        for member in voice_channel_members:
            if ctx.author.id == member["id"]:
                await ctx.respond("Por favor, saia da call primeiro antes de fazer a configuração", ephemeral=True, delete_after=12)
                return

        await ctx.respond(content="", view=helpers_timers.ConfigPomodoro(), ephemeral=True, delete_after=7)


    @discord.slash_command(description="Mostra o rank dos membros mais focados!")
    async def rank(self, ctx):

        self.connection = self.bot.connection
        self.cursor = self.bot.cursor

        global ranking_values

        self.cursor.execute("SELECT * FROM focus_sessions;")
        ranking_values = self.cursor.fetchall()

        embed = discord.Embed(
            title="Painel de Rankings 📊",
            color=discord.Colour.purple(),
        )

        embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")
        embed.add_field(name=" ", value=f" > - Escolha qual tipo de estatística quer ver sobre horas focadas.")

        await ctx.respond(embed=embed, view=helpers_rankings.FocusRankings(), delete_after=20)


    @discord.slash_command(description="Mostra seu status de foco incluindo seus streaks")
    async def foco(self, ctx):

        self.connection = self.bot.connection
        self.cursor = self.bot.cursor
        user_id = ctx.author.id

        # Update inserting last session date if there was one
        self.bot.cursor.execute(
        """
        UPDATE discord_users AS du
            SET last_focus_date = (SELECT focus_datetime
                                    FROM
                                        focus_sessions AS fs
                                    WHERE
                                        fs.user_id = (?)
                                    ORDER BY
                                        fs.focus_datetime DESC
                                    LIMIT 1)
            WHERE
                du.id = (?)
        """, (user_id, user_id))

        self.bot.connection.commit()

        # Query about user streaks
        self.bot.cursor.execute("""
            SELECT 
                du.last_focus_date,
                du.current_focus_streak,
                du.max_focus_streak
            FROM 
                discord_users AS du
            WHERE
                du.id = (?)
        """, (user_id,))

        self.connection.commit()
        streak_data = self.cursor.fetchall()[0]

        # Query on amount of study in total
        self.bot.cursor.execute("""
            SELECT 
                COALESCE(FLOOR(SUM(duration_minutes)/60), 0) as hours,
                COALESCE(SUM(duration_minutes)%60, 0) as minutes
            FROM 
                focus_sessions 
            INNER JOIN 
                discord_users ON user_id = discord_users.id 
            WHERE
                discord_users.id = (?)
        """, (user_id,))

        self.connection.commit()
        total_data = self.cursor.fetchall()[0]

        # Query on amount of study in this month
        self.bot.cursor.execute("""
            SELECT
                COALESCE(FLOOR(SUM(duration_minutes)/60), 0) as hours,
                COALESCE(SUM(duration_minutes)%60, 0) as minutes
            FROM 
                focus_sessions 
            INNER JOIN 
                discord_users on user_id = discord_users.id 
            WHERE 
                MONTH(focus_datetime) = MONTH(NOW()) AND 
                YEAR(focus_datetime) = YEAR(NOW()) AND
                discord_users.id = (?)
            """, (user_id,))
        
        self.connection.commit()
        month_data = self.cursor.fetchall()[0]

        # Query on amount of study in this week
        self.bot.cursor.execute("""
            SELECT
                COALESCE(FLOOR(SUM(duration_minutes)/60), 0) as hours,
                COALESCE(SUM(duration_minutes)%60, 0) as minutes
            FROM
                focus_sessions
            INNER JOIN
                discord_users ON user_id = discord_users.id
            WHERE
                focus_datetime >= DATE_SUB(NOW(), INTERVAL 7 DAY) AND
                discord_users.id = (?)
            """, (user_id,))

        self.connection.commit()
        week_data = self.cursor.fetchall()[0]

        # Query on amount of study in today
        self.bot.cursor.execute("""
            SELECT 
                COALESCE(FLOOR(SUM(duration_minutes)/60), 0) as hours,
                COALESCE(SUM(duration_minutes)%60, 0) as minutes
            FROM 
                focus_sessions
            INNER JOIN 
                discord_users ON user_id = discord_users.id 
            WHERE 
                MONTH(focus_datetime) = MONTH(NOW()) AND
                DAY(focus_datetime) = DAY(NOW()) AND
                discord_users.id = (?)
            """, (user_id,))
        
        self.connection.commit()
        today_data = self.cursor.fetchall()[0]

        embed = discord.Embed(
            color=discord.Colour.purple(),
        )

        embed.set_thumbnail(url=f"{ctx.author.avatar}")

        # streak_data variables
        last_focus_date, current_focus_streak, max_focus_streak = (streak_data[0], streak_data[1], streak_data[2])
        
        streak_data_vars = [last_focus_date, current_focus_streak, max_focus_streak]

        for idx in range(len(streak_data_vars)):
            if streak_data_vars[idx] == None:
                streak_data_vars[idx] = "sem dados"

        time_formatted = ''
        data_formatted = ''

        if streak_data_vars[0] != "sem dados":
            data_formatted = str(streak_data_vars[0]).split(' ')[0]
            time_formatted = str(streak_data_vars[0]).split(' ')[1]
            embed.add_field(name=" ", value=f"**Última sessão:** {data_formatted} às {time_formatted}", inline=False)
        else:
            embed.add_field(name=" ", value=f"**Última sessão:** {streak_data_vars[0]}", inline=False)
        embed.add_field(name=" ", value=f"**Atual streak:** {streak_data_vars[1]}", inline=True)
        embed.add_field(name=" ", value=f"**Maior streak:** {streak_data_vars[2]}", inline=True)

        # total_data variables
        total_hours, total_minutes = (total_data[0], total_data[1])

        embed.title = f"🔥 Foco de {ctx.author.global_name} ({total_hours}**h**{'0' if total_minutes > 0 and total_minutes < 10 else ''}{total_minutes})"

        # month_data variables
        month_hours, month_minutes = (month_data[0], month_data[1])

        # week_data variables
        week_hours, week_minutes = (week_data[0], week_data[1])

        # today_data variables
        today_hours, today_minutes = (today_data[0], today_data[1])

        month = f"**Este mês:** {month_hours}**h**{'0' if month_minutes > 0 and month_minutes < 10 else ''}{month_minutes if month_minutes > 0 else ''}"
        week = f"**Essa semana:** {week_hours}**h**{'0' if week_minutes > 0 and week_minutes < 10 else ''}{week_minutes if week_minutes > 0 else ''}"
        today = f"**Hoje:** {today_hours}**h**{'0' if today_minutes > 0 and today_minutes < 10 else ''}{today_minutes if today_minutes > 0 else ''}"

        embed.add_field(name=" ", value=f"{month}\n{week}\n{today}", inline=False)

        await ctx.respond(embed=embed)


@tasks.loop(seconds=1)
async def study_counter_task(focus_channel, afk_channel):

    global voice_channel_members
    global emojis

    for member in voice_channel_members:

        # normal stopwatch
        # initialization
        if member["message"] == None:
            member["seconds"] = 1
            
            embed = discord.Embed(
            title="",
            description="",
            )

            epoch = time.time()

            if member["pomodoro_enabled"]:

                embed.color = colors[member["pomodoro_color"]]

                embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")
                embed.add_field(name=" ", value=f"> <@{member["id"]}>. Focando! {random.choice(emojis)} \n <t:{int(epoch)}:R> \n 🍅 ({int(member["pomodoro"]/60)}/{int(member["short_break"]/60)}). Fez: {member["current_round"]}")
                embed.set_thumbnail(url=member["avatar"])

                await focus_channel.send(content=f"<@{member["id"]}>", delete_after=1)
                member["message"] = await focus_channel.send(embed=embed)
            
            else:

                embed.color = colors[member["stopwatch_color"]]

                embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")
                embed.add_field(name=" ", value=f"> <@{member["id"]}>. Focando! {random.choice(emojis)} \n <t:{int(epoch)}:R>")
                embed.set_thumbnail(url=member["avatar"])

                await focus_channel.send(content=f"<@{member["id"]}>", delete_after=1)
                member["message"] = await focus_channel.send(embed=embed)
        else:

            # verification in voice channel (either for pomodoro or stopwatch)
            member["limit_counter"] += 1

            if member["limit_counter"] > SEND_VERIFY_MESSAGE_THRESHOLD:

                if not member["on_verify_message_sent"]:
                    # send to dm
        
                    dmchannel = await member["object"].create_dm()

                    embed = discord.Embed(
                        title="🔥 Contagem de foco",
                        description="Confirme sua presença na call dentro de 20 minutos.",
                        color=discord.Colour.purple()
                        )
                    
                    embed.add_field(name=" ", value="|| Você recebeu isso para evitar contar seu foco sem estar focado(a)! ||")

                    success = discord.Embed(
                        title="✅ Sucesso!",
                        description="Obrigado por confirmar sua presença.",
                        color=discord.Colour.green()
                        )

                    failure = discord.Embed(
                        title="❌ Tempo esgotado.",
                        description="Seus 20 minutos já se passaram.",
                        color=discord.Colour.red()
                        )
                    
                    failure.add_field(name=" ", value=" Será movido(a) para a call de inativo.")
                    
                    message = await dmchannel.send(embed=embed)

                    await message.add_reaction(emoji="✅")

                    def check_reaction( r : discord.Reaction, u: discord.Member):

                        if u.bot:
                            return False
                        
                        if r.message != message:
                            return False

                        if r.emoji == "✅":

                            return True
                        else:
                            return False
                    
                    reaction, user = ('','')

                    async def waiting_for_response():
                        try:
                            reaction, user = await member["bot_object"].wait_for(event="reaction_add", check=check_reaction, timeout=WAIT_TO_VERIFY_THRESHOLD)
                            await dmchannel.send(embed=success)
                            print(f"{reaction} por {user}")
                            member["limit_counter"] = 0
                        except TimeoutError:
                            # kick - move to the other VC channel
                            await member["object"].move_to(afk_channel, reason="Não conseguiu verificar presença.")
                            await dmchannel.send(embed=failure)

                    waiting_task = asyncio.create_task(waiting_for_response())
                    member["on_verify_message_sent"] = 1

            # pomodoro feature
            if member["pomodoro_enabled"]:
 
                member["seconds"] += 1

                if not member["on_break"]:
                    
                    if member["seconds"] > member["pomodoro"]:
                        member["on_break"] = 1
                        member["seconds"] = 1
                        member["current_round"] += 1
                        await member["message"].delete()

                        embed = discord.Embed(
                            title="",
                            description="",
                            color=colors[member["break_color"]],
                        )

                        epoch = time.time() + member["short_break"]

                        embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")
                        embed.add_field(name=" ", value=f"> <@{member["id"]}>. Pausa! Ufa... {random.choice(emojis)} \n 🍅 ({int(member["pomodoro"]/60)}/{int(member["short_break"]/60)}). Próximo round: {member["current_round"] + 1} \n <t:{int(epoch)}:R>")
                        
                        if member["pomodoro_image"] != None:

                            embed.set_thumbnail(url=member["pomodoro_image"])

                        else:
                        
                            embed.set_thumbnail(url="https://media.tenor.com/1re8tSKaslIAAAAi/peach-cat-goma.gif")

                        await focus_channel.send(content=f"<@{member["id"]}>", delete_after=1)
                        member["message"] = await focus_channel.send(embed=embed)
                        
                else:

                    # on long break
                    on_long_break = member["current_round"] % member["long_break_interval"] == 0

                    if on_long_break:
                        if member["seconds"] > member["long_break"]:
                            member["message"] = await member["message"].delete()
                            member["on_break"] = 0
                            member["seconds"] = 1

                    # on short break
                    else:
                        if member["seconds"] > member["short_break"]:
                            member["message"] = await member["message"].delete()
                            member["on_break"] = 0
                            member["seconds"] = 1
            else:

                # stopwatch feature
                member["seconds"] += 1


def setup(bot):
    bot.add_cog(Timers(bot))


def register(cursor, connection, member, on_pomodoro_channel, focus_channel, afk_channel, bot):
    try: 
        cursor.execute(
        """
            SELECT 
                pp.pomodoro,
                pp.short_break, 
                pp.long_break, 
                pp.long_break_interval,
                tvp.pomodoro_color,
                tvp.break_color,
                tvp.stopwatch_color,
                tvp.pomodoro_image,
                du.last_focus_date,
                du.current_focus_streak,
                du.max_focus_streak
            FROM 
                pomodoro_preferences AS pp
            INNER JOIN 
                timer_visual_preferences AS tvp ON tvp.user_id = pp.user_id
            INNER JOIN
                discord_users AS du ON du.id = pp.user_id
            WHERE 
                tvp.user_id = (?)

        """, (member.id,))

        member_info = cursor.fetchall()[0]

        voice_channel_members.append({
            "message": None,
            "seconds": 0,
            "seconds_paused": 0,
            "global_name": member.global_name,
            "avatar": member.avatar,
            "id": member.id,
            "object": member,
            "bot_object": bot,

            "pomodoro": member_info[0] * 60, #1500
            "short_break": member_info[1] * 60,
            "long_break": member_info[2] * 60, #900
            "long_break_interval": member_info[3], #4
            "current_round": 0,
            "pomodoro_enabled": 1 if on_pomodoro_channel else 0,
            
            "on_break": 0, # 0,

            "pomodoro_color": member_info[4],
            "break_color": member_info[5],
            "stopwatch_color": member_info[6],
            "pomodoro_image": member_info[7],

            "last_focus_session": member_info[8],
            "current_focus_streak": member_info[9],
            "max_focus_streak": member_info[10],

            "limit_counter": 0,
            "on_verify_message_sent": 0,
            })

        connection.commit()

        if not study_counter_task.is_running():
            study_counter_task.start(focus_channel, afk_channel)
    except Exception as e:
        print(f"{e}")


async def remove(cursor, connection, member, channel):

    member_left = 0
    empty = False

    for index, x in enumerate(voice_channel_members):
        if x["global_name"] == member.global_name:
            member_left = index

    try:
        member_left = voice_channel_members.pop(member_left)

    except:
        print("Empty")
        empty = True

    if not empty:
        if study_counter_task.is_running():
            if len(voice_channel_members) == 0:
                study_counter_task.stop()

            embed = discord.Embed(
            title="",
            description="",
            color=discord.Colour.purple(),
            )

            epoch = time.time()
            
            try:

                # If doesnt have the sufficient time to record
                if member_left["pomodoro_enabled"] and member_left["pomodoro"] * member_left["current_round"] < 60 and not member_left["on_break"] and member_left["seconds"] < 60:
                    await member_left["message"].delete()
                    embed.add_field(name=" ", value=f"{member_left['global_name']}, você deve ficar por pelo menos um minuto para registrar seu tempo!")
                    await channel.send(content=f"<@{member_left["id"]}>", embed=embed, delete_after=5)
                
                elif not member_left["pomodoro_enabled"] and member_left["seconds"] < 60:
                    await member_left["message"].delete()
                    embed.add_field(name=" ", value=f"{member_left['global_name']}, você deve ficar por pelo menos um minuto para registrar seu tempo!")
                    await channel.send(content=f"<@{member_left["id"]}>", embed=embed, delete_after=5)

                else:
                    

                    date = str(datetime.datetime.today()).split('.')[0]
                    user_id = member_left["id"]
                    streak_system_logic(cursor, connection, user_id)
                    embed.set_thumbnail(url=member_left["avatar"])
                    embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")

                    await member_left["message"].delete()

                    if member_left["pomodoro_enabled"]:
                        
                        extra_seconds = member_left["seconds"] if not member_left["on_break"] else 0

                        total_minutes = int((member_left["current_round"] * member_left["pomodoro"] + extra_seconds)/60)

                        total_hours = int(total_minutes/60)

                        if total_hours != 0:

                            if total_minutes % 60 == 0:
                                embed.add_field(name=" ", value=f"O pomodoro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_hours%60} {'**horas**' if total_hours > 1 else '**hora**'}.")
                            
                            else:

                                embed.add_field(name=" ", value=f"O pomodoro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_hours%60} {'**horas**' if total_hours > 1 else '**hora**'} e {total_minutes%60} {'**minutos**' if total_minutes%60 > 1 else '**minuto**'}.")

                        else:

                            embed.add_field(name=" ", value=f"O pomodoro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_minutes} {'**minutos**' if total_minutes%60 > 1 else '**minuto**'}.")

                        cursor.execute("INSERT INTO focus_sessions (focus_datetime, duration_minutes, user_id) VALUES (?, ?, ?)", (date, total_minutes, user_id)) 
                        connection.commit()

                        await channel.send(content=f"<@{member_left["id"]}>", delete_after=1)
                        await channel.send(embed=embed)

                    else:

                        total_minutes = int(member_left["seconds"]/60)
                    
                        total_hours = int(total_minutes/60)

                        if total_hours != 0:

                            embed.add_field(name=" ", value=f"O cronômetro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_hours%60} {'**horas**' if total_hours > 1 else '**hora**'} e {total_minutes%60} {'**minutos**' if total_minutes > 1 else '**minuto**'}.")

                        else:

                            embed.add_field(name=" ", value=f"O cronômetro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_minutes} {'**minutos**' if total_minutes > 1 else '**minuto**'}.")

                        cursor.execute("INSERT INTO focus_sessions (focus_datetime, duration_minutes, user_id) VALUES (?, ?, ?)", (date, total_minutes, user_id)) 
                        
                        connection.commit()

                        await channel.send(content=f"<@{member_left["id"]}>", delete_after=1)
                        await channel.send(embed=embed)
            except:
                pass


def streak_system_logic(cursor, connection, user_id): # TODO: add variable: starting_fucus_session_date

    try: 
        
        # Update inserting last session date if there was one
        cursor.execute(
        """
        UPDATE discord_users AS du
            SET last_focus_date = (SELECT focus_datetime
                                    FROM
                                        focus_sessions AS fs
                                    WHERE
                                        fs.user_id = (?)
                                    ORDER BY
                                        fs.focus_datetime DESC
                                    LIMIT 1)
            WHERE
                du.id = (?)
        """, (user_id, user_id))

        connection.commit()

        cursor.execute("""
            SELECT du.last_focus_date,
                CURDATE() AS today,
                DATE_SUB(CURDATE(), INTERVAL 1 DAY) AS yesterday,
                du.current_focus_streak AS current_streak,
                du.max_focus_streak AS max_streak
            FROM 
                discord_users AS du
            WHERE du.id = (?);
            """, (user_id,))

        dates_info = cursor.fetchall()[0]
        connection.commit()

        last_date = dates_info[0]

        # It doesnt have a last_date. This person never used the study system before
        if last_date == None:
            return

        today = dates_info[1]
        yesterday = dates_info[2]
        current_streak = dates_info[3]
        max_streak = dates_info[4]

        if last_date != today and last_date is not yesterday:
            current_streak = 0
            last_date = today
        
        elif last_date != today and last_date is yesterday:
            last_date = today
            current_streak += 1
            if current_streak > max_streak:
                max_streak = current_streak
        
        elif last_date == today:
            return
        
        cursor.execute("""
            UPDATE 
                discord_users as du
            SET 
                du.last_focus_date = (?)
            SET 
                du.current_focus_streak = (?)
            SET 
                du.max_focus_streak = (?)
            WHERE
                du.id = (?)
                
        """, (last_date, current_streak, max_streak, user_id))

        connection.commit()

    except:
        print("Error, exception at line line 682")
        pass