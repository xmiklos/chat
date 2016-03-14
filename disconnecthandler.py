import asyncore

class DisconnectHandler(asyncore.dispatcher):
	
	def __init__(self, sock):
		asyncore.dispatcher.__init__(self, sock=sock)
		self.send('Maximum number of connections reached. Disconnecting...')
		self.close()
		return

	