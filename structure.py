import aiohttp, asyncio

from datetime import (
	datetime,
	timedelta
)

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

	async def get_tag(self, session, proxies):
		if self.tag is None:
			self.tag = await get_and_parse(session, self.url, proxies=proxies, id='group_post')
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

	async def _get_urls(self, session, proxies):
		global pages_count
		if self.child_urls is None:
			try:
				tag = await get_and_parse(session, self.url, 'a', proxies=proxies, class_='noDecoration')
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

	async def get_items(self, session, proxies):
		if self.items is None:
			self.child_urls = await self._get_urls(session, proxies)
			items = []

			if self.empty is True:
				return items

			self.items = [Item(item_url) for item_url in self.child_urls]

			for f in asyncio.as_completed([item.get_tag(session, proxies) for item in self.items]):
				result = await f

		return self.items


class Group:

	def __init__(self, name, url):
		global SEARCH_STR
		self.url = url
		self.name = name
		self.base_page = self.url + SEARCH_STR
		self.pages = []

	async def get_pages(self, session, proxies, search_terms='', from_='', to_=''):
		max_page = 1
		while (True):
			max_page += 4
			pages_block = [Page(self.base_page % (page_no,search_terms,from_,to_)) for page_no in range(max_page-4, max_page)]
			for f in asyncio.as_completed([page.get_items(session, proxies) for page in pages_block]):
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

	async def get_groups(self, session, proxies, search_terms, to_='', from_=''):
		if self.groups is None:
			tag = await get_and_parse(session, self.url, 'section', proxies=proxies, id='content')

			groups_info = [{'name': url_tag.get_text(), 'url': url_tag.get('href')} for url_tag in tag.select('li > a')]

			self.groups = [Group(info['name'], info['url']) for info in groups_info]

			for f in asyncio.as_completed([group.get_pages(session, proxies, search_terms, from_, to_) for group in self.groups]):
				result = await f
		return self.groups