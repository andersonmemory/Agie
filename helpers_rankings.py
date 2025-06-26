import discord
import mariadb

from dotenv import load_dotenv
import os
load_dotenv()

class FocusRankings(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
    @discord.ui.button(label="Total", style=discord.ButtonStyle.primary, emoji="🥷") 
    async def first_button(self, button, interaction):

        embed = set_button(
            """
                SELECT 
                    ROW_NUMBER() OVER(ORDER BY SUM(duration_minutes) DESC) as ranking, 
                    CONCAT('<@', user_id, '>') as user_id, 
                    FLOOR(SUM(duration_minutes)/60) as hours, 
                    SUM(duration_minutes)%60 as minutes 
                FROM 
                    focus_sessions 
                INNER JOIN 
                    discord_users ON user_id = discord_users.id 
                GROUP BY 
                    (user_id)
                ORDER BY
                    SUM(duration_minutes) DESC
                LIMIT 30;
            """
            , "Top de foco 📊")
        
        await interaction.response.send_message(content="", embed=embed, ephemeral=False, delete_after=7)

    @discord.ui.button(label="Mês", style=discord.ButtonStyle.primary, emoji="👥") 
    async def second_button(self, button, interaction):

        embed = set_button(
            """
                SELECT 
                    ROW_NUMBER() OVER(ORDER BY SUM(duration_minutes) DESC) as ranking, 
                    CONCAT('<@', user_id, '>') as user_id, 
                    FLOOR(SUM(duration_minutes)/60) as hours,
                    SUM(duration_minutes)%60 as minutes
                FROM 
                    focus_sessions 
                INNER JOIN 
                    discord_users on user_id = discord_users.id 
                WHERE 
                    MONTH(focus_datetime) = MONTH(NOW()) AND 
                    YEAR(focus_datetime) = YEAR(NOW()) 
                GROUP BY 
                    (user_id)
                ORDER BY
                    SUM(duration_minutes) DESC
                LIMIT 30;
            """
        , "Top mensal de foco 📊")

        await interaction.response.send_message(content="", embed=embed, ephemeral=False)

    @discord.ui.button(label="Semana", style=discord.ButtonStyle.primary, emoji="🏁") 
    async def third_button(self, button, interaction):

        embed = set_button(
            """
                SELECT
                    ROW_NUMBER() OVER(ORDER BY SUM(duration_minutes) DESC) as ranking,
                    CONCAT('<@', user_id, '>') as user_id,
                    FLOOR(SUM(duration_minutes)/60) as hours,
                    SUM(duration_minutes)%60 as minutes
                FROM
                    focus_sessions
                INNER JOIN
                    discord_users ON user_id = discord_users.id
                WHERE
                    focus_datetime >= DATE_SUB(NOW(), INTERVAL 7 DAY)
                GROUP BY
                    (user_id)
                ORDER BY
                    SUM(duration_minutes) DESC
                LIMIT 30;
            """
        , "Top semana de foco 📊")

        await interaction.response.send_message(content="", embed=embed,ephemeral=False, delete_after=7)

    @discord.ui.button(label="Dia", style=discord.ButtonStyle.primary, emoji="📅")
    async def fourth_button(self, button, interaction):

        embed = set_button(
            """
                SELECT 
                    ROW_NUMBER() OVER(ORDER BY SUM(duration_minutes) DESC) as ranking, 
                    CONCAT('<@', user_id, '>') as user_id, 
                    FLOOR(SUM(duration_minutes)/60) as hours,
                    SUM(duration_minutes)%60 as minutes
                FROM 
                    focus_sessions 
                INNER JOIN 
                    discord_users ON user_id = discord_users.id 
                WHERE 
                    MONTH(focus_datetime) = MONTH(NOW()) AND 
                    DAY(focus_datetime) = DAY(NOW()) 
                GROUP BY 
                    (user_id)
                ORDER BY
                    SUM(duration_minutes) DESC
                LIMIT 30;
            """
        , "Top diário de foco 📊")

        await interaction.response.send_message(content="", embed=embed,ephemeral=False, delete_after=7)

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

def build_list(information):

    ranking_list = [f" #{row[0]} {row[1]}: {row[2]}**h**{'0' if row[3] < 10 else ''}{row[3]}\n" for row in information]

    length = len(ranking_list)

    match length:
        case 1:
            ranking_list[0] = "🥇" + ranking_list[0]
        case 2:
            ranking_list[0] = "🥇" + ranking_list[0]
            ranking_list[1] = "🥈" + ranking_list[1]
        case 3:
            ranking_list[0] = "🥇" + ranking_list[0]
            ranking_list[1] = "🥈" + ranking_list[1]
            ranking_list[2] = "🥉" + ranking_list[2]
        case _:
            ranking_list[0] = "🥇" + ranking_list[0]
            ranking_list[1] = "🥈" + ranking_list[1]
            ranking_list[2] = "🥉" + ranking_list[2]

            for idx, item in enumerate(ranking_list):

                if idx > 2 and idx < 10:
                    ranking_list[idx] = "🟪" + item
                elif idx >= 10:
                    ranking_list[idx] = "" + item

    single_string = "".join(ranking_list)

    return single_string


def set_button(mariadb_query, title):
        
        bot = stabilish_connection()

        bot["cursor"].execute(mariadb_query)

        information = bot["cursor"].fetchall()
        single_string = build_list(information)

        embed = discord.Embed(
            title=title,
            color=discord.Colour.blurple(),
        )

        embed.set_author(name="Mente Ágil", icon_url="https://cdn.discordapp.com/attachments/1219843085341560872/1362999843211186248/Logo_.png?ex=685978c5&is=68582745&hm=59fc7659e42d531a4f663d20ca6e9c0324b2dd7f3ec2d4e9a4d1a5dbd974cf1e&")
        embed.add_field(name=" ", value=f"{single_string}")

        close_connection(bot["connection"], bot["cursor"])
        
        return embed