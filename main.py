import json
import os
import random

import discord
import requests
from discord.ext import commands
from discord.utils import get
from keep_alive import keep_alive
from replit import db


class MyClient(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    async def on_ready(self):
        print("Ready")

    async def on_raw_reaction_add(self, payload):
        self.target_message_id = 1040382544887164989
        if payload.message_id != self.target_message_id:
            return
        guild = client.get_guild(payload.guild_id)

        # print(payload.emoji.name)
        if payload.emoji.name == "🐵":
            role = discord.utils.get(guild.roles, name="Monkey")
            await payload.member.add_roles(role)

        elif payload.emoji.name == "🐱":
            role = discord.utils.get(guild.roles, name="Cat")
            await payload.member.add_roles(role)

        elif payload.emoji.name == "🐶":
            role = discord.utils.get(guild.roles, name="Dog")
            await payload.member.add_roles(role)

    async def on_raw_reaction_remove(self, payload):

        if payload.message_id != self.target_message_id:
            return
        guild = client.get_guild(payload.guild_id)
        member = guild.get_member(payload.user_id)

        if payload.emoji.name == "🐵":
            role = discord.utils.get(guild.roles, name="Monkey")
            await member.remove_roles(role)

        elif payload.emoji.name == "🐱":
            role = discord.utils.get(guild.roles, name="Cat")
            await member.remove_roles(role)

        elif payload.emoji.name == "🐶":
            role = discord.utils.get(guild.roles, name="Dog")
            await member.remove_roles(role)


intents = discord.Intents().all()
client = MyClient(command_prefix="$", intents=intents)


@client.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.RoleNotFound):
        await ctx.send(f"Role not found")

@client.command(pass_context=True, brief="Add a new role to the server", description="Add a new role to the server")
async def addrank(ctx, role_name):
    if ctx.message.author.guild_permissions.administrator:
        guild = ctx.guild
        check_for_duplicate = discord.utils.get(ctx.guild.roles, name=role_name)
        if check_for_duplicate in ctx.guild.roles:
            await ctx.send("That role already exists")
        else:
            await guild.create_role(name=role_name)
            await ctx.send(f"Created role {role_name}")


@client.command(brief="Show all roles", description="Show all roles")
async def ranks(ctx):
    roles = []
    intern = discord.utils.get(ctx.guild.roles, name="Ninja Bot")
    for role in ctx.guild.roles:
        if role < intern and role.name != "@everyone" and role.color == intern.color:
            roles.append(role.name)

    roles = "\n".join(roles)
    embed = discord.Embed(title="Ranks", description=roles, color=0xFF5733)
    await ctx.send(embed=embed)


@client.command(brief="Join or left a role", description="Join or left a role")
async def rank(ctx, role: discord.Role):
    user = ctx.message.author
    if role in ctx.author.roles:
        await user.remove_roles(role)
        await ctx.send(f"You left {role.name}")
    else:
        await user.add_roles(role)
        await ctx.send(f"You joined {role.name}")

sad_words = ["sad", "depressed", "unhappy", "angry", "miserable", "depressing"]

starter_encouragements = ["Cheer up!", "Hang in there.", "you are a great person / bot"]

if "responding" not in db.keys():
    db["responding"] = True


def get_quote():
    response = requests.get("https://zenquotes.io/api/random")
    json_data = json.loads(response.text)
    quote = json_data[0]["q"] + " -" + json_data[0]["a"]
    return quote


def update_encouragements(encouraging_message):
    if "encouragements" in db.keys():
        encouragements = list(db["encouragements"])
        encouragements.append(encouraging_message)
        db["encouragements"] = encouragements
    else:
        db["encouragements"] = [encouraging_message]


def delete_encouragements(index):
    encouragements = list(db["encouragements"])
    if len(encouragements) > index:
        del encouragements[index]
        db["encouragements"] = encouragements


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    msg = message.content

    if msg.startswith("$inspire"):
        quote = get_quote()
        await message.channel.send(quote)

    if db["responding"]:
        options = starter_encouragements
        if "encouragements" in db.keys():
            options = options + list(db["encouragements"])

        if any(word in msg for word in sad_words):
            await message.channel.send(random.choice(options))

    if msg.startswith("$new"):
        encouraging_message = msg.split("$new ", 1)[1]
        update_encouragements(encouraging_message)
        await message.channel.send("New encoraging message added")

    if msg.startswith("$del"):
        encouragements = []
        if "encouragements" in db.keys():
            index = int(msg.split("$del ", 1)[1])
            delete_encouragements(index)
            encouragements = list(db["encouragements"])
            await message.channel.send(encouragements)

    if msg.startswith("$list"):
        encouragements = []
        if "encouragements" in db.keys():
            encouragements = list(db["encouragements"])
            await message.channel.send(encouragements)

    if msg.startswith("$responding"):
        value = msg.split("$responding ", 1)[1]
        if value.lower() == "true":
            db["responding"] = True
            await message.channel.send("Responding is on")
        else:
            db["responding"] = False
            await message.channel.send("Responding is off")

    if msg.startswith("$role"):
        guild = client.get_guild(message.guild_id)
        newrole = msg.split("$new ", 1)[1]
        await message.channel.send("New role added")
        role = discord.utils.get(guild.roles, name=newrole)
        await message.member.add_roles(role)

    else:
        await client.process_commands(message)


keep_alive()
client.run(os.environ["BotKey"])
