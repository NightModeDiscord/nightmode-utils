import os
import re
import traceback
from typing import Iterable

from discord import Color, Embed, Guild, Intents, Message
from discord.ext import commands
from discord.mentions import AllowedMentions

try:
    import dotenv
except ImportError:
    pass
else:
    dotenv.load_dotenv(".env")

os.environ.setdefault("JISHAKU_HIDE", "1")
os.environ.setdefault("JISHAKU_NO_DM_TRACEBACK", "1")
os.environ.setdefault("JISHAKU_NO_UNDERSCORE", "1")
os.environ.setdefault("JISHAKU_RETAIN", "1")


class NightMode(commands.Bot):
    def __init__(self, *, load_extensions=True, loadjsk=True, nightmode_id: int):
        self.nightmode_id = nightmode_id
        self.TESTING = os.environ.get("TESTING", "0") == "1"
        allowed_mentions = AllowedMentions(
            users=True, replied_user=True, roles=False, everyone=False
        )
        super().__init__(
            command_prefix="!",
            intents=Intents.all(),
            allowed_mentions=allowed_mentions,
        )

        if load_extensions:
            self.load_extensions(("cogs.help_command", "cogs.autorole"))
        if loadjsk:
            self.load_extension("jishaku")

    @property
    def nightmode(self) -> Guild:
        nm = self.get_guild(self.nightmode_id)
        if not nm:
            raise RuntimeError("nightmode_id invalid!")
        return nm

    def load_extensions(self, extentions: Iterable[str]):
        for ext in extentions:
            try:
                self.load_extension(ext)
            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)

    async def on_message(self, msg: Message):
        if msg.author.bot:
            return
        await self.process_commands(msg)

    async def on_command_error(
        self, ctx: commands.Context, error: commands.CommandError
    ):
        if isinstance(error, commands.CommandNotFound):
            return
        if isinstance(error, commands.CommandInvokeError):
            await super().on_command_error(ctx, error)
        title = " ".join(re.compile(r"[A-Z][a-z]*").findall(error.__class__.__name__))
        await ctx.send(
            embed=Embed(title=title, description=str(error), color=Color.red())
        )

    async def on_ready(self):
        print("Ready!")


if __name__ == "__main__":

    # Main server
    kwargs = dict(nightmode_id=815176881455497236)

    TESTING = os.getenv("TESTING") == "1"
    if TESTING:
        print("Testing mode")

        # Lab
        kwargs = dict(nightmode_id=831509607146979368)

    bot = NightMode(**kwargs)
    token = os.environ.get("BOT_TOKEN")
    if not token:
        raise RuntimeError("No token set.")
    bot.run(token)
