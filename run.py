import discord
from dotenv import load_dotenv
import os

import random

load_dotenv()

bot = discord.Bot()

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

bot.run(os.getenv("BOT_TOKEN"))