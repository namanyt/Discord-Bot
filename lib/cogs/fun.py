from random import choice, randint
from typing import Optional

from aiohttp import request
from discord import Member, Embed
from discord.ext.commands import Cog, cooldown, BucketType
from discord.ext.commands import command, BadArgument


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='hello', aliases=["hi"])
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(['Hello', 'hey', 'hi'])} {ctx.author.mention} !")

    @command(name='dice', aliases=['roll'])
    @cooldown(1, 60, BucketType.user)
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]
            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)} ")
        else:
            await ctx.send("I cannot calculate that many dices...")
            await ctx.send("type a value smaller than 25.")

    @command(name='slap', aliases=['hit'])
    @cooldown(1, 15, BucketType.guild)
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
        await ctx.send(f"{ctx.author.mention} slapped {member.mention} for {reason}")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("I cannot find anyone with that name")

    @command(name='echo', aliases=['announce'])
    @cooldown(1, 15, BucketType.guild)
    async def echo_message(self, ctx, *, message):
        await ctx.send(message)
        await ctx.message.delete()

    @command(name='fact')
    @cooldown(3, 60, BucketType.guild)
    async def facts(self, ctx, animal: str):
        if animal := animal.lower() in ("dog", "cat", "panda", "fox", "koala", "bird"):
            fact_URL = f"https://some-random-api.ml/facts/{animal}"
            image_URL = f"https://some-random-api.ml/img/{animal if animal != 'bird' else animal}"
            async with request("GET", image_URL, headers={})  as response:
                if response.status == 200:
                    image_data = await response.json()
                    image_link = image_data['link']
                else:
                    image_link = None

            async with request("GET", fact_URL, headers={}) as response:
                if response.status == 200:
                    data = await response.json()

                    embed = Embed(title=f"{animal} Fact",
                                  description=data["fact"],
                                  color=ctx.author.color)
                    if image_link is not None:
                        embed.set_image(url=image_URL)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"API returned a {response.status} status.")
        else:
            await ctx.send(f"Nothing is related to that animal fact")

    @command(name='meme')
    async def send_meme(self, ctx):
        image_URL = "https://some-random-api.ml/meme"
        async with request("GET", image_URL, headers={}) as meme:
            if meme.status == 200:
                image_Data = await meme.json()
                image_link = image_Data['image']
            else:
                image_link = None

        async with request("GET", image_URL, headers={}) as meme_title:
            if meme_title.status == 200:
                Title_data = await meme_title.json()

                embed = Embed(title=Title_data['caption'], color=ctx.author.color)
                if image_link is not None:
                    embed.set_image(url=image_link)
                await ctx.send(embed=embed)
            else:
                await ctx.send(f"API returned a {meme.status} status.")

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
