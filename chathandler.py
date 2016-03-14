import asyncore
import chatclients
#from os import linesep
import time
import re
from titlegetter import TitleGetter
from config import Config

linesep = '\r\n'

class ChatHandler(asyncore.dispatcher):
	
	def __init__(self, sock, server, chunk_size=256):
		self.chunk_size = chunk_size
		asyncore.dispatcher.__init__(self, sock=sock)
		self.data_to_write = ['Please enter your name: ', Config.settings.hello+linesep]
		self.name = ''
		self.server = server
		self.url_re = re.compile(r'www\.(?:[a-zA-Z0-9]+(?:\.[a-zA-Z0-9]+)*)\.[a-zA-Z0-9]+', re.MULTILINE)
		self.user_re = re.compile(r'@(\S+)', re.MULTILINE)
		return
	
	def writable(self):
		response = bool(self.data_to_write)
		return response

	def readable(self):
		return True

	def handle_write(self):
		data = self.data_to_write.pop()
		sent = self.send(data[:self.chunk_size])
		if sent < len(data):
			remaining = data[sent:]
			self.data_to_write.append(remaining)

	def handle_read(self):
		#print 'handle_read'
		data = self.recv(self.chunk_size)
		lines = data.splitlines()
		
		for line in lines:
		
			# ak este nemame meno
			if self.name == '':
				if line == '':
					continue
				else:
					self.name = line
					if not chatclients.ChatClients.new_client(self):
						self.name = ''
						self.data_to_write.append('That name already exist. Disconnecting...')
						while self.writable():
							self.handle_write()
						self.close()
						return
						
			else: # vlastny read
				userlist = self.user_re.findall(line)
				userlist = list(set([x.lower() for x in userlist]))
				urllist = list(set(self.url_re.findall(line)))
				
				titles = ''
				if urllist:
					for url in urllist:
						title = TitleGetter.get(url)
						if title:
							titles = titles + linesep + title
				
				if userlist:
					chatclients.ChatClients.send_to_some(line + titles, userlist, self.name)
				else:
					chatclients.ChatClients.send_to_all(line + titles, self.name)
				
				if titles:
					chatclients.ChatClients.send_to_some(titles.lstrip(), [self.name.lower()])
	
	def handle_close(self):
		while self.writable():
			self.handle_write()
		self.close()
		chatclients.ChatClients.delete_client(self.name)
		if not chatclients.ChatClients.server_exiting and self.name:
			chatclients.ChatClients.send_to_all(self.name, 'Disconnected')
		if self.name:
			print 'Disconnected: '+self.name
		self.server.client_number = self.server.client_number - 1