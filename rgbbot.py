import os
import discord
from dotenv import load_dotenv
from discord.ext import commands
import json
from requests import post, get
import webcolors
from datetime import datetime
from googletrans import Translator


load_dotenv()

TOKEN = os.getenv('TOKEN')
LONG_LIVED_TOKEN = os.getenv('LONG_LIVED_TOKEN')
BASE_URL = os.getenv('BASE_URL')
LIGHT_ENTITY = os.getenv('LIGHT_ENTITY')

url = f"{BASE_URL}api/services/light/turn_on"
url_off = f"{BASE_URL}api/services/light/turn_off"
condition_url = f"{BASE_URL}api/states/binary_sensor.jl_pc_lockscreen"

headers = {
    "Authorization": f"Bearer {LONG_LIVED_TOKEN}",
    "content-type": "application/json",
}

bot = commands.Bot(command_prefix='~')

def get_json_data(r, g, b):
    return f'{{"entity_id": "{LIGHT_ENTITY}", "rgb_color": [{r}, {g}, {b}]}}'


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


def pc_status():
    response = get(condition_url, headers=headers)
    return json.loads(response.text)["state"]


def can_change():
    # off = not changeable / pc turned off
    # on  = changeable / pc turned on
    return pc_status() == "on"


@bot.event
async def on_ready():
    activity = discord.Streaming(name="~help", url="https://www.youtube.com/watch?v=9Deg7VrpHbM")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    print("Bot is ready!")


@commands.cooldown(1, 5, commands.BucketType.user)
@bot.command(
    help="""
    Ändert die Farbe des Lichtes
    Probier es doch mal mit einer Farbe.
    Sehr wahrscheinlich wird die Farbe, die du dir vorstellst, unterstützt ^^
    
    p.s. Englisch hilft ;-)
    """
)
async def light(ctx, *, arg):
    if not can_change():
        embed = discord.Embed(title="Warte noch ein bisschen",
                            description=f"Leider ist das zur Zeit nicht verfügbar, da Jan-Luca nicht an seinem PC sitzt.",
                            color=discord.Colour.orange())
        await ctx.send(embed=embed)
        return

    if arg == "black":
        post(url_off, headers=headers, data=f'{{"entity_id": "{LIGHT_ENTITY}"}}')
        embed = discord.Embed(title="Licht ausgeschaltet", description=f"Du hast das Licht ausgeschaltet.",
                            color=discord.Colour.from_rgb(0, 0, 0))
        await ctx.send(embed=embed)
        return

    try:
        rgb = webcolors.name_to_rgb(arg)
    except ValueError:
        embed = discord.Embed(title="Oh nein!", description="Diese Farbe kenne ich leider nicht :confused:",
                            color=discord.Colour.dark_red(), url="https://www.w3schools.com/cssref/css_colors.asp")
        embed.set_footer(text="p.s. Klicke doch mal auf den Link und informiere dich :)")
        await ctx.send(embed=embed)
        return

    post(url, headers=headers, data=get_json_data(rgb.red, rgb.green, rgb.blue))

    translatedColor = Translator().translate(arg, src='en', dest='de').text
    embed = discord.Embed(title="Farbe geändert", description=f"Du hast die Farbe auf {translatedColor} geändert.",
                        color=discord.Colour.from_rgb(rgb.red, rgb.green, rgb.blue))
    await ctx.send(embed=embed)


@bot.command(help="Aktuelle Lichtinformation")
async def status(ctx):
    if not can_change():
        await ctx.message.add_reaction('☹')
        return

    response = get(url=f"{BASE_URL}api/states/{LIGHT_ENTITY}", headers=headers)
    state = json.loads(response.text)
    rgb = state["attributes"]["rgb_color"]
    r = rgb[0]
    g = rgb[1]
    b = rgb[2]
    actual, closest = get_colour_name((r, g, b))
    embed = discord.Embed(title="Aktuelle Farbe", description=f"Die Farbe ist {closest}.\nSchau links lol.",
                          color=discord.Colour.from_rgb(r, g, b))
    await ctx.send(embed=embed)


@bot.command(
    help="Licht präzise bestimmen"
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
        embed = discord.Embed(title="Oh nein", description="Du hast leider keine Zahl eingegeben.\nDamit kann ich leider nicht viel anfangen :confused: ",
                              color=discord.Colour.dark_red())
        await ctx.send(embed=embed)
        return

    if r < 0 or r > 255 or g < 0 or g > 255 or b < 0 or b > 255:
        embed = discord.Embed(title="Oh nein", description="Ich besitze nicht die Macht, diese Farbe anzuzeigen.",
                              color=discord.Color.dark_red())
        await ctx.send(embed=embed)
        return

    post(url, headers=headers, data=get_json_data(r, g, b))
    embed = discord.Embed(title="Light Info", description=f"You have chosen {r}, {g}, {b}",
                          color=discord.Colour.from_rgb(r, g, b))
    await ctx.send(embed=embed)


@light.error
async def light_error(ctx, error):
    time = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
    print(f"{time} - {error} - {type(error)}")

    if type(error) is discord.ext.commands.errors.CommandOnCooldown:
        embed = discord.Embed(title="Oh nein", description="Du stresst mich so sehr. Warte bitte einen Moment",
                              color=discord.Color.dark_red())
        await ctx.send(embed=embed)
    else:
        await ctx.message.add_reaction('🇳')
        await ctx.message.add_reaction('🇴')


if __name__ == "__main__":
    bot.run(TOKEN)
