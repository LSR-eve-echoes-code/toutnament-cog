from discord.ext import commands
from datetime import datetime
import random
from pd import pd


fn = 'tournament.json'
mf = '%Y%m%d'

def setup(bot):
    l = tournament_cog(bot)
    bot.add_cog(l)
    print('tournament cog loaded')

class tournament_cog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tournament(self, ctx, arg = None):
        if arg == 'contest':
            await self.contest(ctx)
        elif arg == 'loose':
            await self.loose(ctx)
        else:
            await self.bot.send(ctx, 'usage: `.tournament [ contest | loose ]`')

    async def join(self, ctx):
        uid = ctx.author.id
        d = pd(fn)
        if not isinstance(d._dict, dict):
            print('did someone screw up the records? fixing')
            d._dict = {}
            d['p'] = {}
        if str(uid) not in d['p']:
            print(str(uid) in d['p'])
            await self.bot.send(ctx, 'so user <@{}> wants to take part in tournament. ok. lets sign you up'.format(uid))
            d['p'][str(uid)] =  {'rank': 0, 'competitor': None, 'time': None, 'wins': 0, 'losses': 0}
            d.sync()
            await self.bot.send(ctx, 'player <@{}> joined tournament at rank 0'.format(uid))

    async def contest(self, ctx, uid = None):
        await self.join(ctx)
        d = pd(fn)
        if uid == None:
            uid = ctx.author.id
        r = d['p'][str(uid)]
        if r['competitor'] != None:
            await self.bot.send(ctx, 'you are to contest <@{}>. havent killed them yet?'.format(r['competitor']))
            return
        l = [k for k, v in d['p'].items() if v['competitor'] == None and v['rank'] == r['rank'] and k != str(uid)]
        if len(l) == 0:
            await self.bot.send(ctx, 'nobody on your rank. you are too awesome')
            return
        c = random.choices(l)[0]
        r['competitor'] = c
        t = datetime.now().strftime(mf)
        r['time'] = t
        d['p'][str(c)]['time'] = t
        d['p'][str(c)]['competitor'] = uid
        await self.bot.send(ctx, '<@{}>, you are being contested by <@{}>'.format(c, uid))
        d.sync()

    async def loose(self, ctx):
        ret = await self._loose(ctx)
        if ret != None:
            await self.contest(ctx, ret[0])
            await self.contest(ctx, ret[0])

    async def _loose(self, ctx):
        d = pd(fn)
        uid = ctx.author.id
        r = d['p'][str(uid)]
        c = r['competitor']
        if c == None:
            await self.bot.send(ctx, 'you are not contesting anyone atm. say `.tournament contest` to find a random competitor')
            return None
        r['competitor'] = None
        r['time'] = None
        r['rank'] = 0
        cd = d['p'][str(c)]
        cd['competitor'] = None
        cd['time'] = None
        cd['rank'] += 1
        d.sync()
        await self.bot.send(ctx, '<@{}> wins and ascends to rank {}'.format(c, cd['rank']))
        return [uid, c]
