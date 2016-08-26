#Setup Logging
import logging
log = logging.getLogger(__name__)

#Python modules

#Local modules
from ..alarm import Alarm
from ..utils import *

#External modules
import telepot
 
class Telegram_Alarm(Alarm):
 	
	#Gather settings and create alarm
	def __init__(self, settings):
		self.bot_token = settings['bot_token']
 		self.connect()
 		self.chat_id = settings['chat_id']
		self.send_map = parse_boolean(settings.get('send_map', "True"))
		self.title = settings.get('title', "A wild <pkmn> has appeared!")
		self.body = settings.get('body', "<gmaps> \n Available until <24h_time> (<time_left>).")
		self.startup_message = settings.get('startup_message', "True")
		log.info("Telegram Alarm intialized.")
		if parse_boolean(self.startup_message):
			self.client.sendMessage(self.chat_id, 'PokeAlarm activated! We will alert this chat about pokemon.')
	
	#(Re)establishes Telegram connection
	def connect(self):
		self.client = telepot.Bot(self.bot_token) 
 		
	#Send Pokemon Info 
 	def pokemon_alert(self, pkinfo):
		title = replace(self.title, pkinfo)
		body =  replace(self.body, pkinfo)
		args = {
			'chat_id': self.chat_id,
			'text': '<b>' + title + '</b> \n' + body,
			'parse_mode': 'HTML',
			'disable_web_page_preview': 'False',
		}
		if config['SEND'] is not True:
			log.info('Notification turned off')
			return
		try_sending(log, self.connect, "Telegram", self.client.sendMessage, args)
		if self.send_map is True:
			locargs = { 
				'chat_id': self.chat_id,
				'latitude': pkinfo['lat'],
				'longitude':  pkinfo['lng'],
				'disable_notification': 'False'
			}
			try_sending(log, self.connect, "Telegram (loc)", self.client.sendLocation, locargs)
			
		try_sending(log, self.connect, "Telegram", self.client.sendMessage, args)
    #Handle received telegram messages
	def handle(self, msg):
		chat_id = msg['chat']['id']
		content_type, chat_type, chat_id = telepot.glance(msg)
		print(content_type, chat_type, chat_id)
		if content_type == 'location':
			print(msg['location']['longitude'])
			print(msg['location']['latitude'])
			config['LOCATION'] = [msg['location']['latitude'], msg['location']['longitude']]
		elif content_type == 'text':
			split = msg['text'].split( )
			command = split[0]
			if len(split) > 1:
				argument = msg['text'].split( )[1]
			else:
				argument = ''
			print 'Got command: %s' % command
			if command == '/distance':
				self.client.sendMessage(chat_id, 'hallo')
				try:
					config['DISTANCE'] = float(argument)
				except ValueError:
					print "Not a float/distance"                                
                        #print(os.path.join(config['ROOT_PATH'], 'rettig.txt'))
                        #config['GEOFENCE'] = Geofence(os.path.join(config['ROOT_PATH'], 'rettig.txt'))
			elif command == '/geo':
				if argument == '':
					config['GEOFENCE'] = None
				else:
					config['GEOFENCE'] = Geofence(os.path.join(config['ROOT_PATH'], argument))
			elif command == '/startnotification':
				config['SEND'] = True
			elif command == '/stopnotification':
				config['SEND'] = False
