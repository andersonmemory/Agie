import discord
import helpers
import re


class MyModal(discord.ui.Modal,):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.InputText(label="Digite sua passphrase de moderador"))

    # async def callback(self, interaction: discord.Interaction):
    #     interaction.response("Sucesso!", ephemeral=True)

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Modal Results")
        embed.add_field(name=" ", value=self.children[0].value)

class Pomodoro(discord.ui.Modal,):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        
        self.add_item(discord.ui.InputText(label="Tempo do pomodoro (em minutos):"))
        self.add_item(discord.ui.InputText(label="Tempo do short break (em minutos):"))
        self.add_item(discord.ui.InputText(label="Tempo do long break (em minutos):"))
        self.add_item(discord.ui.InputText(label="Quantos rounds para o long_break?"))

    async def callback(self, interaction: discord.Interaction):
        embed = discord.Embed(title="As configurações foram alteradas com sucesso!")
        embed.color = discord.Color.green()
        
        all_values = [self.children[0].value, self.children[1].value, self.children[2].value, self.children[3].value]

        for value in all_values:
            if (int(value) < 0 or int(value) > 255) or not value.isdigit():

                embed.title = "Algo ocorreu errado!"
                embed.color = discord.Colour.red()
                embed.add_field(name=" ", value=f"Você inseriu algum valor que não foi considerado válido", inline=False)

                await interaction.response.send_message(embeds=[embed], ephemeral=True)     

                break
        else:
            embed.add_field(name=" ", value=f"Pomodoro: {self.children[0].value}", inline=False)
            embed.add_field(name=" ", value=f"Short break: {self.children[1].value}", inline=False)
            embed.add_field(name=" ", value=f"Long break: {self.children[2].value}", inline=False)
            embed.add_field(name=" ", value=f"Intervalo para long break: {self.children[3].value}", inline=False)
            
            await interaction.response.send_message(embeds=[embed], ephemeral=True)

class PomoAppearenceImageValidateModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
    
        self.add_item(discord.ui.InputText(label="Insira o link da sua imagem"))

    async def callback(self, interaction: discord.Interaction):

        embed = discord.Embed(title="A imagem foi alterada com sucesso!")
        embed.color = discord.Color.green()

        result = re.search(r"/^(https:)\/\/(c\.tenor\.com)?(media\.tenor\.com)?\/([0-9a-z--_]*)\.(gif$)?(webp$)?/gm", self.children[0].value)

        if result:
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            embed.title = "Algo ocorreu errado!"
            embed.color = discord.Colour.red()
            embed.add_field(name=" ", value=f"Você inseriu algum valor que não foi considerado válido. Apenas gifs do tenor são aceitos.", inline=False)
            embed.add_field(name=" ", value=f"Lembre-se que seu link deve estar no formato: \n ```https://c.tenor.com/1Abcde2fgh34ij/tenor.gif``` \n ou no formato ```https://media.tenor/abcdefgh124-ijkl/mnopq.gif``` \n Peça ajuda no <#1363005746018521118> caso ainda esteja em dificuldades.", inline=False)
            await interaction.response.send_message(embed=embed, ephemeral=True)
