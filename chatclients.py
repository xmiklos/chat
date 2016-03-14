#from os import linesep
from threading import Lock

linesep = '\r\n'

class ChatClients:
	clients = {}
	server_exiting = False
	lock = Lock()
	
	@classmethod
	def new_client(cls, handler):
		cls.lock.acquire()
		if handler.name in cls.clients:
			cls.lock.release()
			return False
		name = handler.name
		cls.clients[name] = handler
		cls.lock.release()
		print 'Connected: '+name
		ChatClients.send_to_all(name, 'Connected', name)
		return True

	@classmethod
	def disconnect_client(cls, name):
		cls.lock.acquire()
		if name in cls.clients:
			handler = cls.clients[name]
			cls.lock.release()
			handler.handle_close()
		else:
			cls.lock.release()
	
	@classmethod
	def delete_client(cls, name):
		cls.lock.acquire()
		if name in cls.clients:
			del cls.clients[name]
		cls.lock.release()
	
	@classmethod
	def disconnect_all(cls):
		cls.server_closing = True
		cls.send_to_all('exiting...', 'Server')
		cls.lock.acquire()
		keys = cls.clients.keys()
		cls.lock.release()
		for name in keys:
			cls.disconnect_client(name)
		
	
	@classmethod
	def send_to_all(cls, message, fromname='', except_name=''):
		cls.lock.acquire()
		prefix = ''
		if bool(fromname):
			prefix = fromname+': '
		if bool(message):
			for name, handler in cls.clients.iteritems():
				if name != fromname and name != except_name:
					handler.data_to_write.append(prefix+message+linesep)
		cls.lock.release()
			
	@classmethod
	def send_to_some(cls, message, to_who_list, fromname=''):
		cls.lock.acquire()
		prefix = ''
		if bool(fromname):
			prefix = fromname+': '
		if bool(message):
			for name, handler in cls.clients.iteritems():
				if name != fromname and name.lower() in to_who_list:
					handler.data_to_write.append(prefix+message+linesep)
		cls.lock.release()