import discord
from dotenv import load_dotenv
import os

load_dotenv()

bot = discord.Bot()

@bot.command(description="Mostra latência do bot")
async def ping(ctx):
    await ctx.respond(f"Pong! A latência é: {bot.latency}")

bot.run(os.getenv("BOT_TOKEN"))