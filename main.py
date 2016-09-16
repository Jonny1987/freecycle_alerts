import requests, logging, re, aiohttp, asyncio, time

from datetime import (
	datetime,
	timedelta
)

from display import display

# TODO extract images and have toggle for filtering out no images
# TODO ordering: by date, group area (google geo),


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
		area = Area('https://www.freecycle.org/browse/UK/London')
		groups = loop.run_until_complete(area.get_groups(session, SEARCH_TERMS, FROM, TO)) 
	display(groups)

async def check_open():
	global open_requests
	global limit
	while(open_requests > limit):
		await asyncio.sleep(0.001)
	return

async def get_and_parse(session, url, *args, **kwargs):
	global open_requests
	await check_open()
	print(open_requests)
	open_requests += 1
	async with session.get(url) as response:
		logging.error('received')
		open_requests -= 1
		if response.status != 200:
			logging.error(str(response.status) + ', ' + url)
		response = await response.read()

	bits = SoupStrainer(args, **kwargs)
	bs = BeautifulSoup(response, 'lxml', parse_only=bits)

	for e in bs:
		if isinstance(e, Doctype):
			e.extract()
			break
	return bs


class Item:

	def __init__(self, url):
		self.url = url
		self.tag = None
		# self.title = _get_title()
		# self.details_tag = _get_details()
		# self.location = _get_location()
		# self.date = _get_datetime()
		# self.desc = _get_desc()
		# self.image = _get_image()

	async def get_tag(self, session):
		if self.tag is None:
			self.tag = await get_and_parse(session, self.url, id='group_post')
		return self.tag

	# def _get_details(self):
	#   return self.tag.select('div#post_details')

	# def _get_location(self):
	#   self.details_tag.find('div').find()
	#   #TODO remove span tags

	# def _get_datetime(self):
	#   date_match = re.search( "(?<=br/> ).*(?=<br)", str(self.tag))
	#   date_str = date_match.group()
		#date_object = datetime.strptime(date_str, '%c')

	#   return date_str

	# def _get_desc():

	# def _get_image(self):


class Page:

	def __init__(self, url):
		self.empty = False
		self.url = url
		self.child_urls = None
		self.size = None
		self.items = None

	async def _get_urls(self, session):
		logging.error('5')
		global pages_count
		if self.child_urls is None:
			try:
				tag = await get_and_parse(session, self.url, 'a', class_='noDecoration')
				logging.error('7')
			except Exception as e:
				logging.error(self.url + ':' + e)
			tags = tag.select('a.noDecoration')
			if len(tags) == 0:
				self.empty = True
				return []

			urls = [tag.get('href') for tag in tags]
			self.child_urls = urls
			self.size = len(urls)

		return urls

	async def get_items(self, session):
		logging.error('3')
		if self.items is None:
			self.child_urls = await self._get_urls(session)
			logging.error('6')
			items = []

			if self.empty is True:
				return items

			self.items = [Item(item_url) for item_url in self.child_urls]

			for f in asyncio.as_completed([item.get_tag(session) for item in self.items]):
				result = await f

		return self.items


class Group:

	def __init__(self, name, url):
		global SEARCH_STR
		self.url = url
		self.name = name
		self.base_page = self.url + SEARCH_STR
		self.pages = []

	async def get_pages(self, session, search_terms='', from_='', to_=''):
		max_page = 1
		while (True):
			max_page += 4
			pages_block = [Page(self.base_page % (page_no,search_terms,from_,to_)) for page_no in range(max_page-4, max_page)]
			for f in asyncio.as_completed([page.get_items(session) for page in pages_block]):
				result = await f

			for page in pages_block:
				if page.empty == True:
					return self.pages

				self.pages.append(page)

				if page.size < 100:	
					return self.pages

class Area:

	def __init__(self, url):
		self.url = url
		self.groups = None

	async def get_groups(self, session, search_terms, to_='', from_=''):
		if self.groups is None:
			tag = await get_and_parse(session, self.url, 'section', id='content')

			groups_info = [{'name': url_tag.get_text(), 'url': url_tag.get('href')} for url_tag in tag.select('li > a')]

			self.groups = [Group(info['name'], info['url']) for info in groups_info]

			for f in asyncio.as_completed([group.get_pages(session, search_terms, from_, to_) for group in self.groups]):
				result = await f
		return self.groups

main()

