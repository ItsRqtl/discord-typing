"""
The main module of the bot.
"""

import logging
import tracemalloc

import discord
from discord.ext import commands

from src.client.logging import InterceptHandler, Logging


class Bot(discord.AutoShardedBot):
    """
    The modified discord bot client.
    """

    def __init__(self) -> None:
        self._client_ready = False
        self.logger = Logging().get_logger()
        logging.basicConfig(
            handlers=[InterceptHandler(self.logger)], level=logging.INFO, force=True
        )

        intents = discord.Intents.default()
        super().__init__(intents=intents)

        for k, v in self.load_extension("src.cogs", recursive=True, store=True).items():
            if v is True:
                self.logger.debug(f"Loaded extension {k}")
            else:
                self.logger.error(f"Failed to load extension {k} with exception: {v}")

    async def on_start(self) -> None:
        """
        The event that is triggered when the bot is started.
        """
        await self.change_presence(activity=discord.Game("typing..."))
        self.logger.info(
            f"""
-------------------------
Logged in as: {self.user.name}#{self.user.discriminator} ({self.user.id})
Shards Count: {self.shard_count}
Memory Usage: {tracemalloc.get_traced_memory()[0] / 1024 ** 2:.2f} MB
 API Latency: {self.latency * 1000:.2f} ms
Guilds Count: {len(self.guilds)}
-------------------------"""
        )

    async def on_ready(self) -> None:
        """
        The event that is triggered when the bot is ready.
        """
        if self._client_ready:
            return
        await self.on_start()
        self._client_ready = True


class BaseCog(commands.Cog):
    """
    The base cog class.
    """

    def __init__(self, bot: Bot) -> None:
        self.bot = bot
        self.client = bot
        self.logger = bot.logger
