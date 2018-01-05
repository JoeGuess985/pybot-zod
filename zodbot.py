
import urllib.request, urllib.parse, json, pickle, re
from lomond.websocket import WebSocket

class client():

	def __init__(self, connect=True, proxies=None):

		self.id 		= ""
		self.owner		= ""
		self.ws 		= None
		self.eventID 	= 1

		self.reconnect_url = ""


		try:
			fp = open("id.cfg", "r")
			self.id = fp.readline()
			self.owner = fp.readline()
			print("id:" + self.id)
			print("owner:" + self.owner)
			fp.close()
		except IOError:
			print("unable to read id.cfg")
			quit()

		try:
			fp = open("token.dat", "rb")
			self.token = fp.readline()
			fp.close()
		except IOError:
			print("unable to read token.dat")
			quit()

		try:
			fp = open("acknowledged.dat", "rb")
			self.acknowledged = pickle.load(fp)
			fp.close()
		except IOError:
			self.acknowledged = []


	def webApiSend(self, contentType, apiMethod, dat=None):

		if dat != None:
			if contentType == "application/json":
				dat = json.dumps(dat).encode('utf8')
			else:
				dat = urllib.parse.urlencode(dat).encode("utf-8")

		header = {"Content-type": contentType, "Authorization": self.token}
		
		req = urllib.request.Request(url='https://slack.com/api/' + apiMethod, headers=header, method='POST', data=dat)
		res = urllib.request.urlopen(req, timeout=5)

		return res.read().decode('utf-8')


	def getRTM(self):
		return self.webApiSend("application/x-www-form-urlencoded", "rtm.connect")


	def acknowledge(self, channel, user):
		self.sendMeMessage(channel, "acknowledges your presence.")

		if user in self.acknowledged:
			return

		self.acknowledged.append(user) 
		fp = open("acknowledged.dat", "wb")
		pickle.dump(self.acknowledged, fp)	#to save to file and load on startup to make it persistant
		fp.close()

	def connect(self):
		rtm = json.loads(self.getRTM())

		self.id = rtm["self"]["id"]
		self.ws = WebSocket(rtm["url"])


	def sendMeMessage(self, channel, msg):
		dat = {"channel": channel, "text": msg}
		self.webApiSend("application/x-www-form-urlencoded", "chat.meMessage", dat)


	def sendMessage(self, channel, msg):
		send = '{"id": ' + str(self.eventID) + ', "type": "message", "channel": "' + channel + '", "text": "' + msg +'"}'
		self.ws.send_text(send)
		self.eventID = self.eventID + 1


	def  messageHandler(self, channel, msg, elevated):

			if not elevated:
				if(msg == "banana"):
					self.sendMessage(channel, "mew mew mew mew mew mew mew. Thats you. Thats what you sound like. deplorable.")
		
				#elevated permissions needed for anything below this point
				return

			if(msg == "banana"):
				self.sendMessage(channel, "orange ya glad I didnt say banana?")

			if(msg == "laputan machine"):
				self.sendMessage(channel, "judas.")
				quit()



	def mainLoop(self):

		for event in self.ws:
			if event.name == "text":
				msg = json.loads(event.text)


				print(msg)

				if "type" in msg:
					if "channel" in msg:
						channel = msg["channel"]
						print("")
						print(channel)
						print("")

					#going to actually need to use this at some point
					if msg["type"] == "reconnect_url":
						self.reconnect_url = msg["url"]

					if msg["type"] == "team_join":
						self.sendMessage(channel, "You There. Kneel Before Zod.")


					if msg["type"] == "message":
						if "subtype" in msg:
							if msg["subtype"] == "me_message":
								if msg["text"] == "kneels":
									self.acknowledge(channel, msg["user"])
															

					#only acknowledged users past this point
						if msg["user"] not in self.acknowledged:
							continue


						#@ message to zod
						if msg["text"][:12] == "<@" + self.id + ">":
							self.messageHandler(channel, msg["text"][13:], msg["user"] == self.owner)





x = client()

x.connect()
x.mainLoop()




#need to get and populate zods id if we are going to catch it for @ messages