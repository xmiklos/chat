import socket
import asyncore
import chathandler
import chatclients

from threading import Thread
from titlegetter import TitleGetter
from disconnecthandler import DisconnectHandler
from config import Config

class ChatServer(asyncore.dispatcher):

	def __init__(self, host, port):
		asyncore.dispatcher.__init__(self)
		self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
		self.set_reuse_addr()
		self.bind((host, port))
		self.listen(5)
		self.tg = Thread(target=TitleGetter.run)
		self.tg.start()
		
		self.client_limit = Config.settings.max
		self.client_number = 0

	def handle_accept(self):
		pair = self.accept()
		
		if pair is not None:
			sock, addr = pair
			self.client_number = self.client_number + 1
			
			if self.client_number > self.client_limit:
				handler = DisconnectHandler(sock)
				self.client_number = self.client_number - 1
			else:
				handler = chathandler.ChatHandler(sock, self)

	def close_server(self):
		TitleGetter.stop()
		self.close()

	@classmethod
	def run(cls):
		asyncore.loop()

if __name__ == "__main__":
	Config.init()
	try:
		server = ChatServer(Config.settings.address, Config.settings.port)
		t = Thread(target=ChatServer.run)
		t.start()
		print 'server started'
		while t.isAlive(): 
			t.join(1)

	except KeyboardInterrupt:
		print 'exiting...'
		chatclients.ChatClients.disconnect_all()
		server.close_server()
		print 'waiting for all to disconnect...'
		t.join()