# Contains a stopwatch and a pomodoro timer for Agie and related functionalities

import discord
from discord.ext import commands, tasks
import time
import datetime
import random

import helpers_rankings, helpers_timers

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

        self.connection = self.bot.connection
        self.cursor = self.bot.cursor

        global bot_connection
        global bot_cursor

        bot_connection = self.connection
        bot_cursor = self.cursor

        # channel that is going to use the focus timers feature
        channel = self.bot.get_channel(1383518749444931661)

        pomodoro_channel = self.bot.get_channel(1384219039626166425)
        stopwatch_channel = self.bot.get_channel(1384219100812939324)

        if before.channel == None:

            on_pomodoro_channel = pomodoro_channel == after.channel
            on_stopwatch_channel = stopwatch_channel == after.channel

            global voice_channel_members
            
            if not member.bot and (on_pomodoro_channel or on_stopwatch_channel):

                self.cursor.execute(
                """
                    SELECT 
                        pp.pomodoro,
                        pp.short_break, 
                        pp.long_break, 
                        pp.long_break_interval,
                        tvp.pomodoro_color,
                        tvp.break_color,
                        tvp.stopwatch_color,
                        tvp.pomodoro_image
                    FROM 
                        pomodoro_preferences AS pp
                    INNER JOIN 
                        timer_visual_preferences AS tvp ON tvp.user_id = pp.user_id
                    WHERE 
                        tvp.user_id = (?)
                """, (member.id,))

                member_info = self.cursor.fetchall()[0]

                voice_channel_members.append({
                    "message": None,
                    "seconds": 0,
                    "seconds_paused": 0,
                    "is_deaf": 1 if member.voice.self_deaf else 0,
                    "global_name": member.global_name,
                    "avatar": member.avatar,
                    "id": member.id,

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
                    "pomodoro_image": member_info[7]
                    })

                self.connection.commit()

            if not study_counter_task.is_running():
                study_counter_task.start(channel)

        elif after.channel == None:

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
                    embed.set_thumbnail(url=member_left["avatar"])
                    embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")

                    await member_left["message"].delete()

                    if member_left["pomodoro_enabled"]:
                        
                        extra_seconds = member_left["seconds"] if not member_left["on_break"] else 0

                        total_minutes = int((member_left["current_round"] * member_left["pomodoro"] + extra_seconds)/60)

                        total_hours = int(total_minutes/60)

                        if total_hours != 0:

                            embed.add_field(name=" ", value=f"O pomodoro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_hours%60} {'**horas**' if total_hours > 1 else '**hora**'} e {total_minutes%60} {'**minutos**' if total_minutes%60 > 1 else '**minuto**'}.")

                        else:

                            embed.add_field(name=" ", value=f"O pomodoro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_minutes} {'**minutos**' if total_minutes%60 > 1 else '**minuto**'}.")

                        self.cursor.execute("INSERT INTO focus_sessions (focus_datetime, duration_minutes, user_id) VALUES (?, ?, ?)", (date, total_minutes, user_id)) 
                        self.connection.commit()

                        await channel.send(content=f"<@{member_left["id"]}>", delete_after=1)
                        await channel.send(embed=embed)

                    else:

                        total_minutes = int(member_left["seconds"]/60)
                    
                        total_hours = int(total_minutes/60)

                        if total_hours != 0:

                            embed.add_field(name=" ", value=f"O cronômetro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_hours%60} {'**horas**' if total_hours > 1 else '**hora**'} e {total_minutes%60} {'**minutos**' if total_minutes > 1 else '**minuto**'}.")

                        else:

                            embed.add_field(name=" ", value=f"O cronômetro parou de contar! \n <@{member_left["id"]}> se concentrou por {total_minutes} {'**minutos**' if total_minutes > 1 else '**minuto**'}.")

                        self.cursor.execute("INSERT INTO focus_sessions (focus_datetime, duration_minutes, user_id) VALUES (?, ?, ?)", (date, total_minutes, user_id)) 
                        
                        self.connection.commit()

                        await channel.send(content=f"<@{member_left["id"]}>", delete_after=1)
                        await channel.send(embed=embed)

    @discord.slash_command(description="altera configurações do pomodoro")
    async def pomodoro(self, ctx):

        # self.connection = self.bot.connection
        # self.cursor = self.bot.cursor


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

@tasks.loop(seconds=1)
async def study_counter_task(channel):

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

                await channel.send(content=f"<@{member["id"]}>", delete_after=1)
                member["message"] = await channel.send(embed=embed)
            
            else:

                embed.color = colors[member["stopwatch_color"]]

                embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")
                embed.add_field(name=" ", value=f"> <@{member["id"]}>. Focando! {random.choice(emojis)} \n <t:{int(epoch)}:R>")
                embed.set_thumbnail(url=member["avatar"])

                await channel.send(content=f"<@{member["id"]}>", delete_after=1)
                member["message"] = await channel.send(embed=embed)
        else:

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

                        epoch = time.time()

                        embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")
                        embed.add_field(name=" ", value=f"> <@{member["id"]}>. Pausa! Ufa... {random.choice(emojis)} \n 🍅 ({int(member["pomodoro"]/60)}/{int(member["short_break"]/60)}). Próximo round: {member["current_round"] + 1} \n <t:{int(epoch)}:R>")
                        
                        if member["pomodoro_image"] != None:

                            embed.set_thumbnail(url=member["pomodoro_image"])

                        else:
                        
                            embed.set_thumbnail(url="https://media.tenor.com/1re8tSKaslIAAAAi/peach-cat-goma.gif")

                        await channel.send(content=f"<@{member["id"]}>", delete_after=1)
                        member["message"] = await channel.send(embed=embed)
                        
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