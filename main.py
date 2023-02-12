from distutils.log import ERROR
from operator import le
import os, requests, json
import discord
from discord.ext import tasks
from discord.ext import commands
from discord.ext.commands import Bot
import urllib3
from dataclasses import dataclass
from typing import Dict, List, Optional
urllib3.disable_warnings()

@dataclass
class Toy:
    identifier: str
    nickname: str
    name: str
    version: str
    battery: int
    status: int

    @staticmethod
    def from_dict(data: dict) -> "Toy":
        return Toy(
            identifier=data["id"],
            nickname=data["nickName"],
            name=data["name"].capitalize(),
            battery=data["battery"],
            status=data["status"],
            version=data["version"],
        )

@dataclass
class Connection:
    device_id: str
    domain: str
    http_port: int
    https_port: int
    platform: str
    app_version: str
    toys: List[Toy]

    @staticmethod
    def from_dict(data: dict) -> "Connection":
        return Connection(device_id=data["deviceId"], domain=data["domain"], http_port=data["httpPort"], https_port=data["httpsPort"], platform=data["platform"], app_version=data["appVersion"], toys=[Toy.from_dict(t) for t in data["toys"].values()],)

def fetch_connections() -> Optional[List[Connection]]:
    result = requests.get("https://api.lovense.com/api/lan/getToys")
    if result.ok:
        data = result.json()
        return [Connection.from_dict(v) for _, v in data.items()]
    return None

bot = discord.Bot()
connections = fetch_connections()
toy = connections[0].toys[0]
id = f"&t={toy.identifier}"


@bot.event
async def on_ready():
    print(f'Logged In As > {bot.user.name}') 


@bot.slash_command()
async def vibrate(ctx, level: int):
    url = f"https://192.168.86.250:30010/Vibrate?v={level}" + id
    if level == 0:
        embed = discord.Embed(description="**Toy Vibration Stopped.**", color=0xffb6c1)
        await ctx.respond(embed=embed)
        r = requests.get(url, verify=False)
    elif level > 20:
        embed = discord.Embed(description="**Toy Vibration Can't Exceed ``20``**", color=0xffb6c1)
        await ctx.respond(embed=embed)
    else: 
        embed = discord.Embed(description=f"**Toy Vibration Set To ``{level}``**", color=0xffb6c1)
        await ctx.respond(embed=embed)
        r = requests.get(url, verify=False)

@bot.slash_command()
async def pattern(ctx, pattern: int):
    url = f"https://192.168.86.250:30010/Preset?v={pattern}" + id
    if pattern == 0:
        embed = discord.Embed(description="**Toy Vibration Stopped.**", color=0xffb6c1)
        await ctx.respond(embed=embed)
        r = requests.get(url, verify=False)
    elif pattern > 4:
        embed = discord.Embed(description="**Toy Pattern Can't Exceed ``4``**", color=0xffb6c1)
        await ctx.respond(embed=embed)
    else:
        pattern_type = ""
        if pattern == 1: 
            pattern_type = "Pulse"
        elif pattern == 2:
            pattern_type = "Wave"
        elif pattern == 3:
            pattern_type = "Fireworks"
        elif pattern == 4:
            pattern_type = "Earthquake"
        embed = discord.Embed(description=f"**Toy Pattern Set To ``{pattern_type}``**", color=0xffb6c1)
        await ctx.respond(embed=embed)
        r = requests.get(url, verify=False)

@bot.slash_command(description="Give Info On The Toy")
async def info(ctx):
    embed = discord.Embed(title="__**Toy Info**__", color=0xffb6c1)
    embed.add_field(name="Name ↓", value=f"```[{toy.name}]```", inline=False)
    embed.add_field(name="Identifier ↓ ", value=f"```[{toy.identifier}]```", inline=False)
    embed.add_field(name="Nickname ↓ ", value=f"```[{toy.nickname}]```", inline=False)
    embed.add_field(name="Battery ↓", value=f"```[{toy.battery}]```", inline=False)
    embed.add_field(name="Version ↓", value=f"```[{toy.version}]```", inline=False)
    embed.set_footer(text=f'Requested By {ctx.author}', icon_url="https://cdn.discordapp.com/attachments/1025892586206003270/1025894159493644368/unknown.png")
    await ctx.respond(embed=embed)


# login
bot.run("token")
