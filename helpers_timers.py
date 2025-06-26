import discord
import modals

import mariadb

from dotenv import load_dotenv
import os
load_dotenv()

color_map = {
    "❤️ Vermelho":"vermelho",
    "🧡 Laranja":"laranja",
    "💛 Amarelo":"amarelo",
    "💚 Verde":"verde",
    "💙 Azul":"azul",
    "💜 Roxo":"roxo",
    "🩷 Rosa":"rosa",
    "🩶 Cinza":"cinza",
    "🖤 Preto":"preto",
    "❓ Aleatório":"aleatório",
}

colors = [ # the list of options from which users can choose, a required field
    discord.SelectOption(
        label="❤️ Vermelho",
    ),
    discord.SelectOption(
        label="🧡 Laranja",
    ),
    discord.SelectOption(
        label="💛 Amarelo",
    ),
    discord.SelectOption(
        label="💚 Verde",
    ),
    discord.SelectOption(
        label="💙 Azul",
    ),
    discord.SelectOption(
        label="💜 Roxo",
    ),
    discord.SelectOption(
        label="🩷 Rosa",
    ),
    discord.SelectOption(
        label="🩶 Cinza",
    ),
    discord.SelectOption(
        label="🖤 Preto",
    ),
    discord.SelectOption(
        label="❓ Aleatório",
        description="Inicia sempre com uma cor diferente."
    ),
]

class ConfigPomodoro(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Configurar", style=discord.ButtonStyle.primary, emoji="⚙️") 
    async def configuration(self, button, interaction):

        pomoModal = modals.Pomodoro(title="Painel de configuração do pomodoro")
        await interaction.response.send_modal(pomoModal)
        await pomoModal.wait()

        pomodoro = pomoModal.children[0].value
        short_break = pomoModal.children[1].value
        long_break = pomoModal.children[2].value
        long_break_interval = pomoModal.children[3].value

        bot = stabilish_connection()

        try:

            bot["cursor"].execute(
                """
                UPDATE 
                    pomodoro_preferences as pp
                SET 
                    pp.pomodoro = (?),
                    pp.short_break = (?),
                    pp.long_break = (?),
                    pp.long_break_interval = (?)
                WHERE 
                    pp.user_id = (?)
                """, (pomodoro, short_break, long_break, long_break_interval, interaction.user.id)
            )

            bot["connection"].commit()
            print("sucess")
        except:
             print("Error, not valid.")

        close_connection(bot["connection"],bot["cursor"])

    @discord.ui.button(label="Aparência", style=discord.ButtonStyle.primary, emoji="🎨") 
    async def appearance(self, button, interaction):

         await interaction.response.send_message("> Escolha agora qual desses dois você quer customizar:", view=AppearanceChooseTimer(), ephemeral=True, delete_after=12)

class AppearanceChooseTimer(discord.ui.View):

    @discord.ui.button(label="Pomodoro", style=discord.ButtonStyle.primary, emoji="🍅") 
    async def pomodoro(self, button, interaction):
    
        await interaction.response.send_message("> Escolha o momento que quer mudar a cor:", view=AppearancePomo(), ephemeral=True, delete_after=12)

    @discord.ui.button(label="Cronômetro", style=discord.ButtonStyle.primary, emoji="⏱️") 
    async def stopwatch(self, button, interaction):
    
        await interaction.response.send_message("", view=AppearanceStopwatch(), ephemeral=True, delete_after=12)

class AppearancePomo(discord.ui.View):

    @discord.ui.button(label="Pomodoro", style=discord.ButtonStyle.primary, emoji="🍅")
    async def pomodoro(self, button, interaction):

        await interaction.response.send_message(f"", view=AppearancePomoPomodoro(), ephemeral=True, delete_after=12)

    @discord.ui.button(label="Break", style=discord.ButtonStyle.primary, emoji="⏸️")
    async def pomodoro_break(self, button, interaction):
        await interaction.response.send_message(f"", view=AppearancePomoBreak(), ephemeral=True, delete_after=12)

class AppearancePomoPomodoro(discord.ui.View):

    @discord.ui.select(placeholder = "Escolha uma cor", min_values = 1, max_values = 1, options = colors)   
    async def select_callback(self, select, interaction):

        bot = stabilish_connection()

        embed = discord.Embed(
                    title="Sucesso!",
                        color=discord.Colour.green(),
                    )
        
        try:

            bot["cursor"].execute(
            """
                UPDATE
                    timer_visual_preferences as tvp
                SET
                    tvp.pomodoro_color = (?)
                WHERE
                    tvp.user_id = (?)
            """, (color_map[select.values[0]], interaction.user.id))

            bot["connection"].commit()

        except mariadb.Error as e:

            embed.title = "Erro!"
            embed.color = discord.Colour.red()
            embed.add_field(name=" ", value="Ocorreu algum erro ao tentar atualizar a cor.")
            close_connection(bot["connection"], bot["cursor"])

            await interaction.response.send_message(content="", embed=embed, ephemeral=True, delete_after=3)
            return
        
        embed.add_field(name=" ", value="A cor foi atualizada.")

        await interaction.response.send_message(content="", embed=embed, ephemeral=True, delete_after=3)

        close_connection(bot["connection"], bot["cursor"])

class AppearancePomoBreak(discord.ui.View):

    @discord.ui.select(placeholder = "Escolha uma cor", min_values = 1, max_values = 1, options = colors)   
    async def select_callback(self, select, interaction):

        bot = stabilish_connection()

        embed = discord.Embed(
                    title="Sucesso!",
                        color=discord.Colour.green(),
                    )

        try:

            bot["cursor"].execute(
            """
                UPDATE
                    timer_visual_preferences as tvp
                SET
                    tvp.break_color = (?)
                WHERE
                    tvp.user_id = (?)
            """, (color_map[select.values[0]], interaction.user.id))

            bot["connection"].commit()

        except mariadb.Error as e:

            embed.title = "Erro!"
            embed.color = discord.Colour.red()
            embed.add_field(name=" ", value="Ocorreu algum erro ao tentar atualizar a cor.")
            close_connection(bot["connection"], bot["cursor"])


            await interaction.response.send_message(content="", embed=embed, ephemeral=True, delete_after=3)
            return

        embed.add_field(name=" ", value="A cor foi atualizada.")

        await interaction.response.send_message(content="", embed=embed, ephemeral=True, delete_after=3)

        close_connection(bot["connection"], bot["cursor"])

class AppearanceStopwatch(discord.ui.View):

    @discord.ui.select( 
        placeholder = "Escolha uma cor",
        min_values = 1,
        max_values = 1,
        options = colors
    )   
    async def select_callback(self, select, interaction):

        bot = stabilish_connection()

        embed = discord.Embed(
                    title="Sucesso!",
                        color=discord.Colour.green(),
                    )

        try:

            bot["cursor"].execute(
            """
                UPDATE
                    timer_visual_preferences as tvp
                SET
                    tvp.stopwatch_color = (?)
                WHERE
                    tvp.user_id = (?)
            """, (color_map[select.values[0]], interaction.user.id))

            bot["connection"].commit()

        except mariadb.Error as e:

            embed.title = "Erro!"
            embed.color = discord.Colour.red()
            embed.add_field(name=" ", value="Ocorreu algum erro ao tentar atualizar a cor.")
            close_connection(bot["connection"], bot["cursor"])


            await interaction.response.send_message(content="", embed=embed, ephemeral=True, delete_after=3)
            return

        embed.add_field(name=" ", value="A cor foi atualizada.")

        await interaction.response.send_message(content="", embed=embed, ephemeral=True, delete_after=3)

        close_connection(bot["connection"], bot["cursor"])

def set_button(mariadb_query, title):
        
        bot = stabilish_connection()

        bot["cursor"].execute(mariadb_query)

        information = bot["cursor"].fetchall()

        embed = discord.Embed(
            title=title,
            color=discord.Colour.blurple(),
        )

        embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")

        close_connection(bot["connection"], bot["cursor"])
        
        return embed

def stabilish_connection():    
    try:
        connection = mariadb.connect(
            user=os.getenv("DB_USER"),
            password=os.getenv("PASSWORD"),
            host=os.getenv("HOST"),
            database=os.getenv("DATABASE")
        )

        cursor = connection.cursor()

        return {"connection":connection, "cursor": cursor}

    except mariadb.Error as e:
        print(f"Couldn't connect to MariaDB server {e}")

def close_connection(connection, cursor):
    connection.close()
    cursor.close()