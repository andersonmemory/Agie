import discord
from discord.ext import commands
import matplotlib.pyplot as plt
import re

async def verify_additional_user_plot(ctx, bot, user : str):
    if user:
        result = re.search(r"[0-9]+", user)
        if result:
            result = int(result.group(0))
            member = bot.get_user(result)
            if member:
                new_plot = create_plot(result, bot.cursor, bot.connection)
                return [new_plot, member]
    
    await ctx.send("Esse usuário não existe ou ocorreu algum outro erro.", delete_after=3)
    return None

class FocusGraphs(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        
    @discord.slash_command(description="Gera um gráfico pessoal do membro")
    async def grafico(self, ctx, user1 : str = None, user2 : str = None):

        self.connection = self.bot.connection
        self.cursor = self.bot.cursor

        first_plot = create_plot(ctx.author.id, self.cursor, self.connection)
        second_plot = None
        third_plot = None

        if user1:
            second_plot = await verify_additional_user_plot(ctx, self.bot, user1)
        
        if user2:
            third_plot = await verify_additional_user_plot(ctx, self.bot, user2)

        fig, ax = plt.subplots()
        ax.plot(first_plot[0], first_plot[1], label=f"{ctx.author.global_name}")

        if user1:
            try:
                ax.plot(second_plot[0][0], second_plot[0][1], label=f"{second_plot[1].global_name}")
                ax.fill_between(second_plot[0][0], second_plot[0][1], alpha=0.5)
            except:
                pass
        
        if user2:
            try:
                ax.plot(third_plot[0][0], third_plot[0][1], label=f"{third_plot[1].global_name}")
                ax.fill_between(third_plot[0][0], third_plot[0][1], alpha=0.5)
            except:
                pass

        ax.set_xlabel('Dias')
        ax.set_ylabel('Horas')

        ax.set_title(f"Tempo de foco de {ctx.author.global_name}{',' if third_plot else ' e '}{f" {second_plot[1].global_name}" if second_plot else '' }{' e ' if third_plot else ''}{third_plot[1].global_name if third_plot else ''}.")
        ax.legend()
        ax.grid()
        ax.fill_between(first_plot[0], first_plot[1], alpha=0.15)

        plt.savefig("graph.jpeg")

        await ctx.send(file=discord.File('graph.jpeg'))

def create_plot(user_id, cursor, connection):

        cursor.execute("""
        SET @initial_date = (
            SELECT DATE(focus_datetime) - INTERVAL 1 DAY
            FROM focus_sessions as fs
            WHERE fs.user_id = (?)
            ORDER BY fs.focus_datetime ASC
            LIMIT 1
            );
        """, (user_id,))
                        
        cursor.execute("SET @end_date = DATE(CURDATE());")

        cursor.execute("""
        SET @difference = (
                SELECT DATEDIFF(@end_date, @initial_date) 
            );
        """)
        
        cursor.execute(
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

        connection.commit()
        
        content = cursor.fetchall()

        x_values = [data_point[0] for data_point in content]
        y_values = [data_point[1] for data_point in content]

        return [x_values, y_values]

def setup(bot):
    bot.add_cog(FocusGraphs(bot))