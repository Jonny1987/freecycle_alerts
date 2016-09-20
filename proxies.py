import requests, aiohttp, 

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
			ip = 'https://' + prox_dict['ip'] + ':' + prox_dict['port']
			ip_list.append(ip)
		return ip_list

	def _change_current(self):
		self.current += 1
		self.current %= self.quantity

	def get_proxy(self):
		self._change_current()
		return self.prox_list[self.current]