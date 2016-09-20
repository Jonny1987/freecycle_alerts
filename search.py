import requests, logging, aiohttp, asyncio, time

from proxies import Proxies

from display import display

from structure import (
	Item,
	Page,
	Group,
	Area,
)

from bs4 import SoupStrainer, BeautifulSoup, Doctype

SEARCH_TERMS = 'desk'
SEARCH_STR = '/posts/search?page=%s&search_words=%s&include_offers=on&include_wanteds=off&date_start=%s&date_end=%s&resultsperpage=100'
FROM = '2016-09-08'
TO = None
open_requests = 0
limit = 10


def main():
	loop = asyncio.get_event_loop()
	with aiohttp.ClientSession(loop=loop) as session:
		proxies = Proxies(session, 30, 'http://gimmeproxy.com/api/getProxy?protocol=http&supportsHttps=true&maxCheckPeriod=3600')
		area = Area('https://www.freecycle.org/browse/UK/London')
		groups = loop.run_until_complete(area.get_groups(session, proxies, SEARCH_TERMS, FROM, TO)) 
	display(groups)


async def get_and_parse(session, url, *args, proxies=None, **kwargs):
	global open_requests
	connector = None
	proxy = None
	if proxies != None:
		proxy = proxies.get_proxy()
	async with session.get(url, proxy=proxy) as response:
		if response.status != 200:
			logging.error(str(response.status) + ', ' + url)
			logging.error(session._connector.proxy)
		response = await response.read()

	bits = SoupStrainer(args, **kwargs)
	bs = BeautifulSoup(response, 'lxml', parse_only=bits)

	for e in bs:
		if isinstance(e, Doctype):
			e.extract()
			break
	return bs


if __name__ == '__main__':
	main()

