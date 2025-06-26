# Contains all the messages Agie will reply.

import discord
from discord.ext import commands

class Messages(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
    
    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        if message.author.bot:
            return
    
        if message.content.lower() == "bom dia":
            await message.reply("Bom dia! <:Cuteanimecatgirlpng:1254070880955404371>", mention_author=True)

        if "agie" in message.content.lower():
            await message.add_reaction(emoji="❤️")

        if "teste" in message.content.lower():
            await message.add_reaction(emoji="✅")

def setup(bot):
    bot.add_cog(Messages(bot))