"""Contains ban and warning functionalities for moderators who must insert a password in order to execute."""

import discord
from discord.ext import commands

from utils import helpers, modals
import datetime

class Moderation(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @discord.slash_command(description="adiciona admin")
    async def add_admin(self, ctx, member, password):

        member_id = ''

        for i in member:
                if i.isdigit():
                    member_id += i   

        try: 
            member_id = int(member_id)
        except:
            member_id = 0

        member_id = int(member_id)

        channel = self.bot.get_channel(1341474955325608017)

        hashed = helpers.hash_password(password=password)

        member = discord.utils.find(lambda m: m.id == member_id, channel.guild.members)

        if member:
            self.bot.cursor.execute("INSERT IGNORE INTO moderators (user_id, password) VALUES (?, ?)", (member_id, hashed))
            self.bot.connection.commit()
        else:
            ctx.respond("Membro não existe!", ephemeral=True)
            return

        await ctx.respond("Adicionado!", ephemeral=True)

    @discord.slash_command(description="Reporta warn em um usuário.")
    async def warn(self, ctx, usuario: str, motivo: str):

        channel = self.bot.get_channel(1382123737368756355)

        warn_limit = 3

        self.connection = self.bot.connection
        self.cursor = self.bot.cursor

        myModal = modals.MyModal(title="Painel do moderador.")

        await ctx.send_modal(myModal)
        await myModal.wait()
        password = bytes(myModal.children[0].value, 'utf-8')

        self.cursor.execute("SELECT user_id, password FROM moderators;")
        moderators_list = [[x[0], bytes(x[1], 'utf-8')] for x in self.bot.cursor.fetchall()]
        
        member_id = ''
        
        for i in usuario:
            if i.isdigit():
                member_id += i
        
        try:
            member_id = int(member_id)
        except:
            member_id = 0
        
        member = self.bot.get_user(member_id)

        if member:
            if helpers.check_password(password=password, author_id=ctx.author.id, moderators_list=moderators_list):
                
                date = str(datetime.datetime.today()).split('.')[0]

                self.bot.cursor.execute("INSERT INTO warns (warn_datetime, reason, user_id) VALUES (?, ?, ?)", (date, motivo, member_id))
                self.bot.connection.commit()

                self.bot.cursor.execute("SELECT COUNT(*) FROM warns WHERE user_id = (?)", (member_id,))
                warn_counter = self.cursor.fetchall()[0][0]
                print(warn_counter)

                embed = discord.Embed(
                    title=f"Advertência",
                    description=f"Warn {warn_counter} de {warn_limit}",
                    color=discord.Colour.yellow(),
                )
                
                embed.add_field(name="", value=f"**Moderador responsável**: <@{ctx.author.id}>", inline=False)
                embed.add_field(name="", value=f"**Usuário advertido**: {usuario}", inline=False)
                embed.add_field(name="Motivo:", value=f"{motivo}", inline=False)

                member = discord.utils.find(lambda m: m.id == member_id, channel.guild.members)

                await ctx.respond(f"{usuario} foi advertido(a).")
                
                await channel.send("", embed=embed)

            else:
                await ctx.respond("Senha incorreta.", ephemeral=True)

        else:
            await ctx.respond("Esse usuário não existe.", ephemeral=True)
            return

    @discord.slash_command(description="Reporta banimento em um usuário.")
    @discord.default_permissions(ban_members=True)
    async def ban(self, ctx, usuario: str, motivo: str):

        channel = self.bot.get_channel(1382123737368756355)

        self.connection = self.bot.connection
        self.cursor = self.bot.cursor

        myModal = modals.MyModal(title="Painel do moderador.")

        await ctx.send_modal(myModal)
        await myModal.wait()
        password = bytes(myModal.children[0].value, 'utf-8')

        self.cursor.execute("SELECT user_id, password FROM moderators;")
        moderators_list = [[x[0], bytes(x[1], 'utf-8')] for x in self.bot.cursor.fetchall()]

        member_id = ''

        for i in usuario:
            if i.isdigit():
                member_id += i

        try:
            member_id = int(member_id)
        except:
            member_id = 0

        member = self.bot.get_user(member_id)

        if member:
            if helpers.check_password(password=password, author_id=ctx.author.id, moderators_list=moderators_list):
                
                embed = discord.Embed(
                    title=f"Banimento",
                    color=discord.Colour.red(),
                )
                
                embed.add_field(name="", value=f"**Moderador responsável**: <@{ctx.author.id}>", inline=False)
                embed.add_field(name="", value=f"**Usuário banido**: {usuario}", inline=False)
                embed.add_field(name="Motivo:", value=f"{motivo}", inline=False)

                await ctx.respond(f"{usuario} foi banido(a).")
                await channel.send("", embed=embed)

                member = discord.utils.find(lambda m: m.id == member_id, channel.guild.members)
                await member.ban(delete_message_seconds=0, reason=motivo)

            else:
                await ctx.respond("Senha incorreta.", ephemeral=True)

        else:
            await ctx.respond("Esse usuário não existe.", ephemeral=True)
            return

def setup(bot):
    bot.add_cog(Moderation(bot))