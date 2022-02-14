import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import json
from requests import post, get
import webcolors

load_dotenv()
TOKEN = os.getenv('TOKEN')
LONG_LIVED_TOKEN = os.getenv('LONG_LIVED_TOKEN')
BASE_URL = os.getenv('BASE_URL')

url = f"{BASE_URL}api/services/light/turn_on"
url_off = f"{BASE_URL}api/services/light/turn_off"
test_url = f"{BASE_URL}api/states/input_boolean.discord_rgb"
headers = {
    "Authorization": f"Bearer {LONG_LIVED_TOKEN}",
    "content-type": "application/json",
}

bot = commands.Bot(command_prefix='~')

def getData(r, g, b):
    return f'{{"entity_id": "light.schreibtisch", "rgb_color": [{r}, {g}, {b}]}}'

def getData2(r, g, b):
    return f'{{"entity_id": "light.arbeitszimmer", "rgb_color": [{r}, {g}, {b}]}}'

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return actual_name, closest_name

def can_change():
    response = get(test_url, headers=headers)
    state = json.loads(response.text)["state"]
    return state == "on"

@bot.event
async def on_ready():
    activity = discord.Streaming(name="~help", url="https://www.youtube.com/watch?v=9Deg7VrpHbM")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Bot is ready!")

@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command(
    help="""
    Verfügbare Farben:
    🔴 \u2794 red
    🟢 \u2794 green
    🔵 \u2794 blue
    🟣 \u2794 purple
    ⚪ \u2794 white
    🟡 \u2794 yellow
    ⚫ \u2794 black
    """
)
async def light(ctx, *, arg):

    if not can_change():
        await ctx.message.add_reaction('☹')
        return

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

@bot.command(help="guvken wie licht izzzz")
async def status(ctx):

    if not can_change():
        await ctx.message.add_reaction('☹')
        return

    response = get(url = f"{BASE_URL}api/states/light.schreibtisch", headers=headers)
    state = json.loads(response.text)
    rgb = state["attributes"]["rgb_color"]
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    actual, closest = get_colour_name((r, g, b))
    embed = discord.Embed(title="Aktuelle Farbe", description=f"Die Farbe ist {closest}.\nSchau links lol.", color=discord.Colour.from_rgb(r, g, b))
    await ctx.send(embed=embed)

@bot.command(
    help="""
    Licht präzise bestimmen
    """
)
async def light_fancy(ctx, r, g, b):

    if not can_change():
        await ctx.message.add_reaction('☹')
        return

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

@light.error
async def light_error(ctx, error):
    print(error)
    await ctx.message.add_reaction('🇳')
    await ctx.message.add_reaction('🇴')

bot.run(TOKEN)