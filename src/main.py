import discord
from discord.ext import commands, tasks
import asyncio
import logging
from datetime import datetime, timedelta
import os

# Intents setup
intents = discord.Intents.default()
intents.members = True

# Bot setup
bot = commands.Bot(command_prefix="!", intents=intents)

# Environment variables
TOKEN = os.getenv("DISCORD_BOT_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))
DELAYED_ROLE_ID = int(os.getenv("DISCORD_DELAYED_ROLE_ID"))
RULES_CHANNEL_ID = int(os.getenv("DISCORD_RULES_CHANNEL_ID"))
WELCOME_CHANNEL_ID = int(os.getenv("DISCORD_WELCOME_CHANNEL_ID"))

logging.basicConfig(level=logging.INFO)

def create_overlay(member):
    # Example function: implement your custom overlay logic here
    from PIL import Image, ImageDraw, ImageFont

    base_image = Image.open("media/avatar.png")
    draw = ImageDraw.Draw(base_image)
    font = ImageFont.load_default()

    draw.text((10, 10), f"Welcome {member.name}!", fill="white", font=font)
    base_image.save("media/output.png")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    check_roles.start()

@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return
    logging.info(f'User joined: {member.name} ({member.id})')

    # Save avatar and create overlay
    try:
        await member.display_avatar.save("media/avatar.png")
        create_overlay(member)
    except Exception as e:
        logging.error(f"Error saving avatar or creating overlay: {e}")

    # Send welcome message with image
    try:
        with open("media/output.png", "rb") as fobj:
            picture = discord.File(fobj)
            await member.send(
                f'Hello {member.mention}, welcome!\n'
                f'Please read the <#{RULES_CHANNEL_ID}> first, thanks!',
                file=picture)
    except Exception as e:
        logging.error(f"Error sending welcome message: {e}")

    # Send welcome message in the guild's channel
    guild = bot.get_guild(GUILD_ID)
    if guild:
        await guild.get_channel(WELCOME_CHANNEL_ID).send(f'{member.mention} ({member.id}) joined')

    # Wait for 1 hour and assign the delayed role
    await asyncio.sleep(3600)
    delayed_role = guild.get_role(DELAYED_ROLE_ID)
    if delayed_role:
        await member.add_roles(delayed_role)
        logging.info(f"Assigned delayed role {delayed_role.name} to {member.name}")

@tasks.loop(hours=24)
async def check_roles():
    guild = bot.get_guild(GUILD_ID)
    if not guild:
        return

    delayed_role = guild.get_role(DELAYED_ROLE_ID)
    if not delayed_role:
        logging.error("Delayed role not found")
        return

    now = datetime.utcnow()
    for member in guild.members:
        if delayed_role not in member.roles:
            time_in_guild = now - member.joined_at
            if time_in_guild >= timedelta(hours=1):
                await member.add_roles(delayed_role)
                logging.info(f"Assigned delayed role {delayed_role.name} to {member.name} during daily check")

bot.run(TOKEN)
