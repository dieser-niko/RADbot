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

logging.basicConfig(level=logging.INFO)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    check_roles.start()

@bot.event
async def on_member_join(member):
    if member.guild.id != GUILD_ID:
        return
    logging.info(f'User joined: {member.name} ({member.id})')

    # Wait for 1 hour and assign the delayed role
    await asyncio.sleep(3600)
    guild = bot.get_guild(GUILD_ID)
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
