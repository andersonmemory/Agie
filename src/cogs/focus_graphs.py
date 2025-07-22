"""Contains commands to create plots based on user data on the focus counting system."""
from __future__ import annotations

import discord
from discord.ext import commands
import matplotlib.pyplot as plt
from PIL import Image
import re
import os

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import mariadb


async def verify_additional_user_plot(ctx, bot, user : str):
    """Verify if user is capable of creating a plot based on his data

    Args:
        ctx (discord.ApplicationContext): the original message context.
        bot (discord.Bot): a Bot instance.
        user (str): the Discord user ID as a string.

    Returns:
        [new_plot, member]: a list of two items, the plot object and the member object that was validated.
        Returns None if either user never used the focus counting system or doesn't exist in the server.
    """

    if user:
        result = re.search(r"[0-9]+", str(user))
        if result:
            result = int(result.group(0))
            member = bot.get_user(result)
            if member:
                new_plot = create_plot(result, bot.cursor, bot.connection)
                if new_plot:
                    return [new_plot, member]
                else:
                    await ctx.send(f"> ⚠️ : {member.global_name} ainda não tem registro de tempo de foco.", delete_after=15)
                    return None
    
    await ctx.send("> ⚠️ : Esse usuário não existe ou ocorreu algum outro erro.", delete_after=15)
    return None


class FocusGraphs(commands.Cog):
    """Contains all commands related to plots 
        generation based on user data.
    """

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="Gera um gráfico pessoal do membro")
    @discord.option("membro1", description="O primeiro membro para o gráfico")
    @discord.option("membro2", description="O segundo membro para o gráfico")
    async def grafico(self, ctx, membro1 : str = None, membro2 : str = None):
        """Generates a plot based on the member that executed and may also
        create plots for each member represented in 'membro1' and 'membro2'.

        Args:
            ctx (discord.ApplicationContext): Discord context object.
            membro1 (str, optional): The first member for the plot to be generated. Defaults to None.
            membro2 (str, optional): The second member for the plot to be generated. Defaults to None.
        """
        self.connection = self.bot.connection
        self.cursor = self.bot.cursor

        fig, ax = plt.subplots()

        first_plot = create_plot(int(ctx.author.id), self.cursor, self.connection)

        second_plot = None
        third_plot = None

        if membro1:
            second_plot = await verify_additional_user_plot(ctx, self.bot, membro1)
        
        if membro2:
            third_plot = await verify_additional_user_plot(ctx, self.bot, membro2)

        create_plot(ctx.author.id, self.cursor, self.connection)


        if first_plot:
            ax.plot(first_plot[0], first_plot[1], label=f"{ctx.author.global_name}")
            ax.fill_between(first_plot[0], first_plot[1], alpha=0.15)
        else:
            await ctx.send("> ⚠️ : você ainda não tem registro de tempo de foco.")


        if membro1 and second_plot:
            try:
                ax.plot(second_plot[0][0], second_plot[0][1], label=f"{second_plot[1].global_name}")
                ax.fill_between(second_plot[0][0], second_plot[0][1], alpha=0.5)
            except:
                print("Error")
        
        if membro2 and third_plot:
            try:
                ax.plot(third_plot[0][0], third_plot[0][1], label=f"{third_plot[1].global_name}")
                ax.fill_between(third_plot[0][0], third_plot[0][1], alpha=0.5)
            except:
                print("Error")

        ax.set_xlabel('Dias', color="white")
        ax.set_ylabel('Horas', color="white")
        ax.tick_params(labelsize=10, colors="white", labelrotation=30)


        if not (second_plot or third_plot):
            ax.set_title(f"Tempo de foco de {ctx.author.global_name}.")
        else:
            ax.set_title(f"Tempo de foco de {ctx.author.global_name}{', ' if third_plot else ' e '}{f"{second_plot[1].global_name}" if second_plot else '' }{' e ' if third_plot else ''}{third_plot[1].global_name if third_plot else ''}.")
        
        ax.title.set_color("white")

        fig.set_facecolor("#71268f")
        ax.legend()
        ax.grid()
        ax.set_facecolor("#71268f")

        plt.savefig("graph.png", transparent=True)

        img1 = Image.open("assets/bg_graph.png")
        img2 = Image.open("graph.png")

        final = Image.alpha_composite(img1, img2)

        final.save("result.png")

        file = discord.File("result.png", filename="result.png")

        embed = discord.Embed(
        color=discord.Colour.purple(),
        )

        embed.set_image(url="attachment://result.png")

        await ctx.respond(embed=embed, file=file)

        os.remove("result.png")
        os.remove("graph.png")


def create_plot(user_id : int, cursor : mariadb.Cursor, connection : mariadb.Connection):
        """Creates a plot for the specified user and returns a list with
        x_axis and y_axis  of the generated plot.

        Args:
            user_id (int): Discord user identifier.
            cursor (mariadb.Cursor): Database cursor for SQL operations.
            connection (mariadb.Connection): Database connection object.

        Returns:
            [x_values, y_values]: a list containing x_axis and y_axis values to be used
            to generate a plot.

        """

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
            COALESCE(FORMAT(fs.hours, 2), 0) AS hours
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
                (SUM(fdt.duration_minutes)/60) AS hours,
                SUM(fdt.duration_minutes)%60 AS minutes,
                fdt.focus_datetime
            FROM 
                focus_sessions AS fdt
            WHERE
                user_id = (?)
            GROUP BY
                DATE(fdt.focus_datetime)) AS fs
        ON
            DATE(fs.focus_datetime) = dt.dates
        ORDER BY
            dt.dates;

        """, (user_id,))

        connection.commit()
        
        content = cursor.fetchall()

        if content[0][0] == None:
            return None

        x_values = [data_point[0] for data_point in content]
        y_values = [float(data_point[1]) for data_point in content]

        return [x_values, y_values]


def setup(bot):
    bot.add_cog(FocusGraphs(bot))