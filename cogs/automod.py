import contextlib
import string
import uuid

from discord import Member, NotFound
from discord.ext.commands import Cog, Context, Greedy, command, has_guild_permissions

printable = set(string.printable)

from bot import NightMode


class AutoMod(Cog):
    def __init__(self, bot: NightMode):
        self.bot = bot

    @command()
    @has_guild_permissions(administrator=True)
    async def scannames(self, ctx: Context):
        for m in ctx.guild.members:
            await self.auto_nick_member(
                m, reason="AutoMod Action - Requested by {}".format(ctx.author)
            )

    @command()
    @has_guild_permissions(manage_nicknames=True)
    async def modnick(self, ctx: Context, *, members: Greedy[Member], reason: str):
        for m in members:
            await self.moderate_nick(
                m, "Requested by {} | {}".format(ctx.author, reason)
            )

    @Cog.listener("on_member_join")
    async def nickname(self, member: Member):
        await self.auto_nick_member(member)

    async def auto_nick_member(self, member: Member, *, reason="AutoMod Action"):
        if self.check_nick(member):
            await self.moderate_nick(member, reason)

    @staticmethod
    async def check_nick(member: Member):
        username = member.display_name
        name = "".join([c for c in username if c in printable])
        return username != name or len(name) < 3 or name[0] == "!"

    @staticmethod
    async def moderate_nick(member: Member, reason: str = None):
        diff = str(uuid.uuid1())[:6]
        with contextlib.suppress(NotFound):
            await member.edit(nick="Moderated Nickname {}".format(diff), reason=reason)


def setup(bot: NightMode):
    bot.add_cog(AutoMod(bot))
