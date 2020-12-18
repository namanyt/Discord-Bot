from random import choice, randint
from typing import Optional

from discord import Member
from discord.ext.commands import Cog
from discord.ext.commands import command, BadArgument


class Fun(Cog):
    def __init__(self, bot):
        self.bot = bot

    @command(name='hello', aliases=["hi"])
    async def say_hello(self, ctx):
        await ctx.send(f"{choice(['Hello', 'hey', 'hi'])} {ctx.author.mention} !")

    @command(name='dice', aliases=['roll'])
    async def roll_dice(self, ctx, die_string: str):
        dice, value = (int(term) for term in die_string.split("d"))

        if dice <= 25:
            rolls = [randint(1, value) for i in range(dice)]
            await ctx.send(" + ".join([str(r) for r in rolls]) + f" = {sum(rolls)} ")
        else:
            await ctx.send("I cannot calculate that many dices...")
            await ctx.send("type a value smaller than 25.")

    @command(name='slap', aliases=['hit'])
    async def slap_member(self, ctx, member: Member, *, reason: Optional[str] = "no reason"):
        await ctx.send(f"{ctx.author.mention} slapped {member.mention} for {reason}")

    @slap_member.error
    async def slap_member_error(self, ctx, exc):
        if isinstance(exc, BadArgument):
            await ctx.send("I cannot find anyone with that name")

    @command(name='echo', aliases=['announce'])
    async def echo_message(self, ctx, *, message):
        await ctx.send(message)
        await ctx.message.delete()

    @Cog.listener()
    async def on_ready(self):
        if not self.bot.ready:
            self.bot.cogs_ready.ready_up("fun")


def setup(bot):
    bot.add_cog(Fun(bot))
