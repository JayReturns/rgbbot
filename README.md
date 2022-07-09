# Discord RGB Bot

Discord bot that changes (my) light in Home Assistant

Start with `python rgbbot.py`

## Configuration
Create a file called `.env` and supply the following values:
* `TOKEN`  
Your Discord bot token
* `LONG_LIVED_TOKEN`  
Your Long Lived Token from Home Assistant
* `BASE_URL`  
The URL to your Home Assistant with a trailing "/"
* `LIGHT_ENTITY`  
The light entity to change with the commands