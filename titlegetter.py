from Queue import Queue
from threading import Event,Thread
from urllib2 import urlopen
import re
import httplib

class TitleGetter:
	
	q = Queue()
	
	@classmethod
	def run(cls):
	
		regex = re.compile('<title>(.*?)</title>', re.IGNORECASE|re.DOTALL)
		
		while True:
			item = cls.q.get(1);
			
			if item is not None:

				# get title
				try:
					c = httplib.HTTPConnection(item.url)
					c.request("GET", "/")
					r = c.getresponse()

					if r.status == 200:
						data = r.read()
						title = regex.search(data).group(1)
					c.close()
				except:
					title = ''
				
				item.result = title
				item.notify()
			else:
				break

	@classmethod
	def stop(cls):
		cls.q.put(None)
		
	@classmethod
	def get(cls, url):
		a = cls(url)
		return a.get_result()
		
	def __init__(self, url):
		self.url = url
		self.result = None
		self.event = Event()
		TitleGetter.q.put(self)

	def get_result(self):
		self.event.wait()
		
		return self.result

	def notify(self):
		self.event.set()

if __name__ == "__main__":
	t = Thread(target=TitleGetter.run)
	t.start()
	a = TitleGetter('www.fi.muni.cz')
	print a.get_result()