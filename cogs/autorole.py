from discord import CustomActivity, Forbidden, Member, NotFound, Role
from discord.ext.commands import Cog, Context, command, has_guild_permissions

from bot import NightMode


class AutoRole(Cog):
    def __init__(self, bot: NightMode, *, supporter_role_id: int):
        self.bot = bot
        self.supporter_role_id = supporter_role_id

    @property
    def supporter_role(self) -> Role:
        supporter_role = self.bot.nightmode.get_role(self.supporter_role_id)
        if not supporter_role:
            raise RuntimeError("Invalid supporter_role_id configured.")
        return supporter_role

    @Cog.listener("on_member_update")
    async def manage_supporter_role(self, before: Member, after: Member):
        act = after.activity

        if not isinstance(act, CustomActivity):
            return await self.remove_supporter_role(after)

        if not act.name or "gg/nightmode" not in act.name.lower():
            return await self.remove_supporter_role(after)

        if self.supporter_role in after.roles:
            return

        try:
            await after.add_roles(self.supporter_role)
        except (NotFound, Forbidden):
            pass

    async def remove_supporter_role(self, member: Member):
        if self.supporter_role in member.roles:
            try:
                await member.remove_roles(self.supporter_role)
            except (NotFound, Forbidden):
                pass

    @command(aliases=["supscan"])
    @has_guild_permissions(administrator=True)
    async def supporterscan(self, ctx: Context):
        await ctx.send("Starting scan!")
        added = 0
        failed = 0

        supporter_role = self.supporter_role
        for m in ctx.guild.members:
            act = m.activity
            if (
                isinstance(act, CustomActivity)
                and act.name
                and "gg/nightmode" in act.name.lower()
                and supporter_role not in m.roles
            ):
                try:
                    await m.add_roles(supporter_role)
                except (NotFound, Forbidden):
                    failed += 1
                else:
                    added += 1

        await ctx.send(
            f"Added supporter role to {added} members, failed to add to {failed}"
        )


def setup(bot: NightMode):
    kwargs = dict(supporter_role_id=831812661166997514)
    if bot.TESTING:
        kwargs = dict(supporter_role_id=831829864306049044)
    bot.add_cog(AutoRole(bot, **kwargs))
