import asyncio, aiohttp, logging, requests

from bs4 import SoupStrainer, BeautifulSoup

class Proxies():
	"""Creates and stores list of ProxyConnetors and rotates proxies"""
	def __init__(self, session, quantity, url):
		self.session = session
		self.quantity = quantity
		self.url = url
		self.prox_list = self._get_ips()
		self.current = 0

	def make_prox_list(self):
		prox_list = []
		ip_list = self._get_ips()
		for ip in ip_list:
			connector = aiohttp.ProxyConnector(proxy=ip)
			prox_list.append(connector)
		return prox_list


	def _get_ips(self):
		ip_list = []
		prox_dict = {}
		while(('http://' + prox_dict.get('ip', '') + str(prox_dict.get('port', ''))) not in ip_list and len(ip_list) < self.quantity):
			response = requests.get(self.url)
			prox_dict = response.json()
			ip = 'http://' + prox_dict['ip'] + ':' + prox_dict['port']
			ip_list.append(ip)
			logging.error(ip_list)
		logging.error('wwww')	
		return ip_list

	def _change_current(self):
		self.current += 1
		self.current %= self.quantity

	def get_proxy(self):
		self._change_current()
		return self.prox_list[self.current]

async def get_and_parse(session, url, *args, proxies=None, **kwargs):
	proxy = None
	if proxies != None:
		proxy = proxies.get_proxy()
	#await check_open()
	# print(open_requests)
	# open_requests += 1
	import ipdb; ipdb.set_trace()
	async with session.get(url, proxy=proxy) as response:
		logging.error('received')
		logging.error('received')
		# open_requests -= 1
		#global last_time
		# time_now = time.time()
		# logging.error(time_now - last_time)
		# last_time=time_now
		# if page_type:
		# 	print_count(url, page_type)
		if response.status != 200:
			logging.error(str(response.status) + ', ' + url)
			logging.error(session._connector.proxy)
		response = await response.read()

async def stuff(session, url, proxies):
	result = await get_and_parse(session, url, proxies=proxies, id='group_post')
	print(result)

loop = asyncio.get_event_loop()
with aiohttp.ClientSession(loop=loop) as session:
	proxies = Proxies(session, 1, 'http://gimmeproxy.com/api/getProxy?protocol=http&supportsHttps=true&maxCheckPeriod=3600')
	groups = loop.run_until_complete(stuff(session, 'https://www.freecycle.org/browse/UK/London', proxies))

