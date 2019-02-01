import aiohttp
import json

from urllib.parse import urlencode
from discord.ext.commands import command

class OEIS:

	@command()
	async def oeis(self, ctx, *, query=''):
		with ctx.typing():
			async with aiohttp.ClientSession() as session:
				params = {
					'q': query,
					'start': 0,
					'fmt': 'json'
				}
				async with session.get('https://oeis.org/search', params=params, timeout=10) as req:
					j = await req.json()
					# print(json.dumps(j, indent=4))
					count = j.get('count', 0)
					res = j.get('results', None)
					if count == 0:
						await ctx.send('No sequences were found.')
					elif res is None:
						await ctx.send(f'There are {count} relavent sequences. Please be more specific.')
					else:
						name = res[0]['name']
						number = res[0]['number']
						digits = res[0]['data'].replace(',', ', ').strip()
						m = f'There were {count} relavent sequences. Here is one:\n\n**{name}**\nhttps://oeis.org/A{number}\n\n{digits}\n'
						# for c in res[0]['comment']:
						# 	if len(m) + len(c) + 10 < 2000:
						# 		m += f'\n> {c}'
						await ctx.send(m)


def setup(bot):
	bot.add_cog(OEIS())