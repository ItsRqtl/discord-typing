"""
Cog module for the slash commands.
"""

from typing import Union

import aiofiles
import discord
import orjson
from discord.ext import tasks

from src.client.i18n import I18n, option, slash_command
from src.main import BaseCog, Bot


class Commands(BaseCog):
    """
    The cog class for the slash commands.
    """

    def __init__(self, bot: Bot) -> None:
        super().__init__(bot)
        self._channels = None
        self.typing_task.start()

    @tasks.loop(seconds=5)
    async def typing_task(self) -> None:
        """
        The typing task.
        """
        if self._channels is None:
            async with aiofiles.open("storage/typing.json", "rb") as f:
                self._channels = orjson.loads(await f.read())
        updated = self._channels.copy()
        for c in self._channels:
            try:
                if channel := self.bot.get_channel(c):
                    await channel.trigger_typing()
            except Exception:
                updated.remove(c)
        if updated != self._channels:
            async with aiofiles.open("storage/typing.json", "wb") as f:
                await f.write(orjson.dumps(self._channels))

    @slash_command("start")
    @option(
        "start",
        "channel",
        channel_types=[
            discord.ChannelType.text,
            discord.ChannelType.news,
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.voice,
        ],
        required=False,
    )
    @discord.guild_only()
    @discord.default_permissions(manage_channels=True)
    async def start(
        self,
        ctx: discord.ApplicationContext,
        channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread] = None,
    ) -> None:
        """
        Start typing in a channel.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param channel: The channel to start typing in.
        :type channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]
        """
        await ctx.defer(ephemeral=True)
        channel = channel or ctx.channel
        is_thread = hasattr(channel, "parent") and channel.parent
        if (is_thread and not channel.permissions_for(ctx.guild.me).send_messages_in_threads) or (
            not is_thread and not channel.permissions_for(ctx.guild.me).send_messages
        ):
            await ctx.respond(I18n.get("slash.start.no_permission", ctx, channel=channel.mention))
            return
        if channel.id in self._channels:
            await ctx.respond(I18n.get("slash.start.already_typing", ctx, channel=channel.mention))
            return
        else:
            self._channels.append(channel.id)
            async with aiofiles.open("storage/typing.json", "wb") as f:
                await f.write(orjson.dumps(self._channels))
            await ctx.respond(I18n.get("slash.start.success", ctx, channel=channel.mention))
            await channel.trigger_typing()

    @slash_command("stop")
    @option(
        "stop",
        "channel",
        channel_types=[
            discord.ChannelType.text,
            discord.ChannelType.news,
            discord.ChannelType.news_thread,
            discord.ChannelType.public_thread,
            discord.ChannelType.private_thread,
            discord.ChannelType.voice,
        ],
        required=False,
    )
    @discord.guild_only()
    @discord.default_permissions(manage_channels=True)
    async def stop(
        self,
        ctx: discord.ApplicationContext,
        channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread] = None,
    ) -> None:
        """
        Stop typing in a channel.

        :param ctx: The context of the command.
        :type ctx: discord.ApplicationContext
        :param channel: The channel to stop typing in.
        :type channel: Union[discord.TextChannel, discord.VoiceChannel, discord.Thread]
        """
        await ctx.defer(ephemeral=True)
        channel = channel or ctx.channel
        if channel.id not in self._channels:
            await ctx.respond(I18n.get("slash.stop.not_typing", ctx, channel=channel.mention))
            return
        else:
            self._channels.remove(channel.id)
            async with aiofiles.open("storage/typing.json", "wb") as f:
                await f.write(orjson.dumps(self._channels))
            await ctx.respond(I18n.get("slash.stop.success", ctx, channel=channel.mention))
        await channel.trigger_typing()


def setup(bot: Bot) -> None:
    """
    The setup function of the cog.
    """
    bot.add_cog(Commands(bot))
