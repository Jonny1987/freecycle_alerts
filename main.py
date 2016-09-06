import requests, logging, re, aiohttp, asyncio	

from datetime import (
	datetime,
	timedelta
)

# TODO extract images and have toggle for filtering out no images
# TODO ordering: by date, group area (google geo),


from bs4 import SoupStrainer, BeautifulSoup

SEARCH_TERMS = 'desk'
SEARCH_STR = '/posts/search?page=%ssearch_words=%s&include_offers=on&include_wanteds=off&date_start=%s&date_end=%s&resultsperpage=100'

def display(groups):
	results = {}
	for group in groups:
		results[group.name] = [item.get_tag() for page in group.get_pages() for item in page.get_items()]

	for term, urls in results_map.items():
		print(term + ':' + str(urls))

def main():
	loop = asyncio.get_event_loop()  
	area = Area('https://www.freecycle.org/browse/UK/London', SEARCH_TERMS)
	loop.run_until_complete(area.get_groups()) 

	display(groups)

async def parse(url, *args, **kwargs):
	response = await aiohttp.request('GET', url)
	response = await response.text()

	bits = SoupStrainer(args, **kwargs)
	bs = BeautifulSoup(response, 'lxml', parse_only=bits)

	return bs


class Item:

	def __init__(self, url):
		logging.error('creating Item')
		self.url = url
		self.tag = None
		# self.title = _get_title()
		# self.details_tag = _get_details()
		# self.location = _get_location()
		# self.date = _get_datetime()
		# self.desc = _get_desc()
		# self.image = _get_image()

	async def get_tag(self):
		if self.tag is None:
			self.tag = await parse(self.url, id='group_post')

		return self.tag


	# def _get_details(self):
	# 	return self.tag.select('div#post_details')

	# def _get_location(self):
	# 	self.details_tag.find('div').find()
	# 	#TODO remove span tags

	# def _get_datetime(self):
	# 	date_match = re.search( "(?<=br/> ).*(?=<br)", str(self.tag))
	# 	date_str = date_match.group()
	# 	#date_object = datetime.strptime(date_str, '%c')

	# 	return date_str

	# def _get_desc():

	# def _get_image(self):


class Page:

	def __init__(self, url):
		logging.error('creating Page')
		self.empty = False
		self.url = url
		self.child_urls = None
		self.size = None
		self.items = None

	async def _get_urls(self):
		if self.child_urls is None:
			tag = await parse(self.url, 'a', class_='noDecoration')
			tags = tag.select('a.noDecoration')

			if len(tags) == 0:
				self.empty = True
				return []

			urls = [tag.get('href') for tag in tags]

			self.child_urls = urls
			self.size = len(urls)

		return urls

	async def get_items(self):
		if self.items is None:
			self.child_urls = await self._get_urls()

			items = []

			if self.empty is True:
				return items

			self.items = [Item(item_url) for item_url in self.child_urls]

			for item in self.items:
				await item.get_tag()

		return self.items


class Group:

	def __init__(self, url, name, search_terms='', from_='', to_=''):
		logging.error('creating Group')
		global SEARCH_STR
		self.from_ = from_
		self.to_ = to_
		self.search_terms = search_terms
		self.url = url
		self.name = name
		self.base_page = self.url + SEARCH_STR
		self.pages = None

	async def get_pages(self):
		if self.pages is None:
			pages = []

			page_no = 0
			while (True):
				page_no += 1
				page = Page(self.base_page % (page_no,self.search_terms,self.from_,self.to_))
				await page.get_items()
				if page.empty == True:
					break

				pages.append(page)

				if page.size < 100:
					break

			self.pages = pages

		return self.pages

class Area:

	def __init__(self, url, search_terms, from_=None, to_=None):
		logging.error('creating Area')
		self.url = url
		self.search_terms = search_terms
		self.groups = None

	async def get_groups(self):
		if self.groups is None:
			tag = await parse(self.url, 'section', id='content')

			groups_info = [{'name': url_tag.get_text(), 'url': url_tag.get('href')} for url_tag in tag.select('li > a')]

			self.groups = [Group(info['url'], info['name'], self.search_terms) for info in groups_info]

			for group in self.groups:
				await group.get_pages()
				groups.append(group)

		return self.groups

main()

