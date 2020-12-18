from asyncio import sleep
from pathlib import Path

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from discord import Intents, HTTPException, Forbidden
from discord.ext.commands import Bot as BotBase, Context
from discord.ext.commands import (CommandNotFound, BadArgument, MissingRequiredArgument)

PREFIX = "?"
OWNER_IDS = [584227289592496129]
COGS = [p.stem for p in Path(".").glob("./lib/cogs/*.py")]
IGNORE_EXCEPTIONS = (CommandNotFound, BadArgument)

from ..db import db


class Ready(object):
    def __int__(self):
        for cog in COGS:
            setattr(self, cog, False)

    def ready_up(self, cog):
        setattr(self, cog, True )
        print(f"{cog} cog ready")

    def all_ready(self):
        return all([getattr(self, cog) for cog in COGS])


class Bot(BotBase):
    def __init__(self):
        self.PREFIX = PREFIX
        self.ready = False
        self.cogs_ready = Ready()

        self.guild = None
        self.scheduler = AsyncIOScheduler()

        db.autosave(scheduler=self.scheduler)

        super().__init__(command_prefix=PREFIX,
                         owner_ids=OWNER_IDS,
                         intents=Intents.all())

    def setup(self):
        for cog in COGS:
            self.load_extension(f"lib.cogs.{cog}")
            print(f"{cog} cog is loaded")

        print("Set Completed...")

    def run(self, version):
        self.VERSION = version

        print("running setup...")
        self.setup()

        with open("./lib/bot/token.0", "r", encoding='utf-8') as tf:
            self.TOKEN = tf.read()

        print("running bot...")
        super().run(self.TOKEN, reconnect=True)

    async def process_commands(self, message):
        ctx = await self.get_context(message, cls=Context)

        if ctx.command is not None and ctx.guild is not None:
            if self.ready:
                await self.invoke(ctx)

            else:
                await ctx.send("I'm not ready to receive commands.")
                await ctx.send("please wait")

    async def rule_reminder(self):
        await self.stdout.send("remember the rule... !")

    async def on_connect(self):
        print('bot connected')

    async def on_disconnected(self):
        print('bot disconnected')

    async def on_error(self, err, *args, **kwargs):
        if err == "on_command_error":
            await args[0].send('Something went wrong.')

        await self.stdout.send("An error has spawned")

        raise

    async def on_command_error(self, ctx, exc):
        if any([isinstance(error, exc) for error in IGNORE_EXCEPTIONS]):
            pass

        elif isinstance(exc, MissingRequiredArgument):
            await ctx.send("Command is incomplete")

        elif isinstance(exc.original, HTTPException):
            await ctx.send("Unable to send Message")

        elif isinstance(exc.original, Forbidden):
            await ctx.send("I dont have the permission to that...")

        else:
            raise exc

    async def on_ready(self):
        if not self.ready:
            self.guild = self.get_guild(584228344262819851)
            self.scheduler.add_job(self.rule_reminder, CronTrigger(day_of_week=0, hour=12, minute=0, second=0))
            self.stdout = self.get_channel(584228344262819853)
            self.scheduler.start()
            await self.stdout.send("Bot is Online !")

            while not self.cogs_ready.all_ready():
                await sleep(0.5)

            self.ready = True
            print("Bot is Ready")
        else:
            print("bot reconnected")

    async def on_message(self, message):
        if not message.author.bot:
            await self.process_commands(message)


bot = Bot()
