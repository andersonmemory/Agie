import discord
from dotenv import load_dotenv
import os

import random

load_dotenv()

intents = discord.Intents.default()
intents.members = True 

bot = discord.Bot(intents=intents)

@bot.event
async def on_connect():
     print(f"{bot.user.name} connected.")

@bot.command(description="Mostra latência do bot")
async def ping(ctx):
    await ctx.respond(f"Pong! A latência é: {bot.latency}")

@bot.command(description="Diz um número aleatório entre dois valores")
async def number(ctx, inicial: int, final: int):
    value = random.randint(inicial, final)
    await ctx.respond(f"Seu número aleatório é: {value}")

@bot.event
async def on_member_join(member: discord.Member):
    guild = member.guild
    if (
        guild.system_channel is not None
    ):  # For this to work, System Messages Channel should be set in guild settings.
        await guild.system_channel.send(f"Seja muito bem-vindo(a) {member.mention}! <:Cuteanimecatgirlpng:1254070880955404371> ")
        await guild.system_channel.send(f"<:Keystra:1254073239877980171>")
        await guild.system_channel.send(f"Você pode colocar uma cor no seu nick em <#1341590988996739132>. Só reagir clicando no emoji correspondente! ❤️")

bot.run(os.getenv("BOT_TOKEN"))