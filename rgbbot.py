import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
from requests import post

load_dotenv()
TOKEN = os.getenv('TOKEN')
LONG_LIVED_TOKEN = os.getenv('LONG_LIVED_TOKEN')
BASE_URL = os.getenv('BASE_URL')

url = f"{BASE_URL}api/services/light/turn_on"
url_off = f"{BASE_URL}api/services/light/turn_off"
headers = {
    "Authorization": f"Bearer {LONG_LIVED_TOKEN}",
    "content-type": "application/json",
}

bot = commands.Bot(command_prefix='~')

def getData(r, g, b):
    return f'{{"entity_id": "light.schreibtisch", "rgb_color": [{r}, {g}, {b}]}}'

def getData2(r, g, b):
    return f'{{"entity_id": "light.arbeitszimmer", "rgb_color": [{r}, {g}, {b}]}}'

 
@bot.event
async def on_ready():
    activity = discord.Streaming(name="~help", url="https://www.youtube.com/watch?v=9Deg7VrpHbM")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Bot is ready!")

@commands.cooldown(1, 10, commands.BucketType.default)
@bot.command(
    help="""
    Verfügbare Farben:
    🔴\u2794 red
    🟢\u2794 green
    🔵\u2794 blue
    🟣 \u2794 purple
    ⚪ \u2794 white
    🟡 \u2794 yellow
    ⚫ \u2794 black
    """
)
async def light(ctx, *, arg):

    if arg == 'red':
        post(url, headers=headers, data=getData(255, 0, 0))
        post(url, headers=headers, data=getData2(255, 0, 0))
        await ctx.message.add_reaction('🔴')
    elif arg == 'blue':
        post(url, headers=headers, data=getData(0, 0, 255))
        post(url, headers=headers, data=getData2(0, 0, 255))
        await ctx.message.add_reaction('🔵')
    elif arg == 'yellow':
        post(url, headers=headers, data=getData(255, 255, 0))
        post(url, headers=headers, data=getData2(255, 255, 0))
        await ctx.message.add_reaction('🟡')
    elif arg == 'green':
        post(url, headers=headers, data=getData(0, 255, 0))
        post(url, headers=headers, data=getData2(0, 255, 0))
        await ctx.message.add_reaction('🟢')
    elif arg == 'purple':
        post(url, headers=headers, data=getData(127, 0, 255))
        post(url, headers=headers, data=getData2(127, 0, 255))
        await ctx.message.add_reaction('🟣')
    elif arg == 'white':
        post(url, headers=headers, data=getData(255, 255, 255))
        post(url, headers=headers, data=getData2(255, 255, 255))
        await ctx.message.add_reaction('⚪')
    elif arg == 'black':
        post(url_off, headers=headers, data='{"entity_id": "light.schreibtisch"}')
        post(url_off, headers=headers, data='{"entity_id": "light.arbeitszimmer"}')
        await ctx.message.add_reaction('⚫')
    else:
        embed = discord.Embed(title="Dumm?", description="Du solltest dich besser über die Farben informieren...", color=discord.Colour.dark_red())
        await ctx.send(embed = embed)
        return

@bot.command(
    help="""
    Licht präzise bestimmen
    """
)
async def light_fancy(ctx, r, g, b):
    
    try:
        r = int(r)
        g = int(g)
        b = int(b)
    except ValueError:
        embed = discord.Embed(title="Dumm?", description="Du musst schon Zahlen eingeben du depp...", color=discord.Colour.dark_red())
        await ctx.send(embed=embed)
        return

    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
        embed = discord.Embed(title="Dumm?", description="Wie soll ich diese Farbe bitte anzeigen???", color=discord.Color.dark_red())
        await ctx.send(embed=embed)
        return

    post(url, headers=headers, data=getData(r, g, b))
    embed = discord.Embed(title="Light Info", description=f"You have chosen {r}, {g}, {b}", color=discord.Colour.from_rgb(r, g, b))
    await ctx.send(embed=embed)

bot.run(TOKEN)