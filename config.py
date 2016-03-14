import argparse
import ConfigParser

class Config:

	settings = None

	@classmethod
	def init(cls):
		config = ConfigParser.SafeConfigParser()
		config.read("config.ini")
		
		parser = argparse.ArgumentParser()
		parser.add_argument('--address', default=config.get('server', 'address'))
		parser.add_argument('--port', default=config.get('server', 'port'), type=int)
		parser.add_argument('--max', default=config.get('server', 'max'), type=int)
		parser.add_argument('--hello', default=config.get('server', 'hello'))
		
		cls.settings = parser.parse_args()