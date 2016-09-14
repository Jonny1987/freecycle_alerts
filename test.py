import asyncio, aiohttp, logging

from bs4 import SoupStrainer, BeautifulSoup

async def stuff():
	async with session.get('http://www.whoishostingthis.com/tools/user-agent/') as response:
		if response.status != 200:
			logging.error(str(response.status))
		response = await response.read()
	bits = SoupStrainer('div')
	bs = BeautifulSoup(response, 'lxml', parse_only=bits)
	print(bs)

loop = asyncio.get_event_loop()
with aiohttp.ClientSession(loop=loop) as session:
	groups = loop.run_until_complete(stuff())

