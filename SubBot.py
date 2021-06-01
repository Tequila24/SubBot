# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import random
import json
from pprint import pprint
from datetime import datetime
from SubDB import SubDB
from VkLib import VkLib
from FagModule import FagModule
from LogModule import LogModule
from pathlib import Path
import re

creatorID = 19155229
confID = 2000000001
testConfID = 2000000004

dices = {1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤', 6: '⑥'}

class SubBot:

	def __init__(self):
		self.token, self.group_id = self.load_settings_from_file()

		self.VkLib = VkLib(self.token, self.group_id)

		self.dBase = SubDB("Sub24Conference")
		self.Faggots = FagModule(self.dBase, self.VkLib, self.group_id)
		self.Logs = LogModule(self.dBase, self.VkLib)

#		chat_members = self.VkLib.get_chat_members(confID, self.group_id)
#		for member_id in chat_members:
#			self.dBase.add_user(member_id, chat_members[member_id])
#		pprint(self.dBase.get_users_list())
		print('I am awake')

	def __exit__(self):
		print('bye')
		del self.dBase
		del self.VkLib

	def load_settings_from_file(self):
		token: str = "0"
		group_id: int = 0

		settings_file_path = Path('./settings.txt')
		if settings_file_path.is_file():
			file = open(settings_file_path, 'r')
			lines = file.readlines()
			for line in lines:
				if 'token=' in line:
					token = line[6:].strip()
				if 'group_id=' in line:
					group_id = int(line[9:].strip())
		print(token, group_id)
		return token, group_id

	def check_is_for_me(self, message_text: str):
		if len(message_text) > 5:
			if 'sub24' in message_text[:5]:
				return True, message_text[5:]
			elif 'суб24' in message_text[:5]:
				return True, message_text[5:]
			elif 'бот' in message_text[:3]:
				return True, message_text[3:]
			elif 'bot' in message_text[:3]:
				return True, message_text[3:]
		return False, ''

	def reply_help(self, peer_id: int):
		message_text: str = '''
		Список доступных команд:\n
		помощь - вывести список доступных команд\n
		эхо - повторить сообщение\n
		%d\д% - бросить кости в стиле 1d20, где 1 - количество костей, 20 - количество граней. Максимальные значения - 999\n
		логи таймер - показать время с последних логов\n
		логи сброс - сбросить дату последних логов на текущую\n
		кто пидор - показать пидора на сегодня\n
		топ пидоров - показать таблицу лидеров-пидеров\n
		'''
		self.VkLib.reply(peer_id, message_text)

	def echo(self, peer_id: int, message: str):
		self.VkLib.reply(peer_id, '>' + message.strip())
				
	def reply_dice(self, peer_id: int, author_id: int, dices_amount, dice_value):
		if ( (dices_amount<1) or (dice_value<2) ):
			self.VkLib.reply(peer_id, "Количество костей должно быть больше 0, а значение - больше 1")
			return

		if ( (dices_amount>999) or (dice_value>999) ):
			self.VkLib.reply(peer_id, "превышен лимит")
			return

		reply_text = "@{0} ".format(self.VkLib.get_user_domain_by_id(author_id))		
		for i in range(dices_amount):
			reply_text += " " + str(random.randrange(1, dice_value+1))
		self.VkLib.reply(peer_id, reply_text)

	def run(self):

		for event in self.VkLib.longpoll.listen():
			try:
				if event.type == VkLib.VkBotEventType.MESSAGE_NEW:

					json_event = json.loads(json.dumps(dict(event.object)))
					author_id = int(json_event['from_id'])
					peer_id = int(json_event['peer_id'])
					message_text = str(json_event['text']).lower().strip()

#					if peer_id != testConfID:
#						continue

					is_for_me, message_text = self.check_is_for_me(message_text)
					if not is_for_me:
						continue
					message_text = message_text.strip()

					if 'помощь' in message_text:
						self.reply_help(peer_id)

					if 'эхо' in message_text[:3]:
						self.echo(peer_id, message_text[3:])

					if 'статус' in message_text:
						self.VkLib.reply(peer_id, "Lock'd and loaded, ready to roll")

					match = re.match(r'(-?\d+)[DdДд](-?\d+)', message_text)
					if (match):
						dices_amount = int(match.group(1))
						dice_value = int(match.group(2))
						self.reply_dice(peer_id, author_id, dices_amount, dice_value)

					if 'логи' in message_text:
						if 'таймер' in message_text:
							self.Logs.get_logs_timer(peer_id)
						if 'сброс' in message_text:
							self.Logs.reset_logs_timer(peer_id)

					if 'кто пидор' in message_text:
						self.Faggots.check_today_fag(peer_id)

					if 'топ пидоров' in message_text:
						self.Faggots.show_fag_stats(peer_id)

			except Exception as e:
				self.VkLib.reply(testConfID, "COMMAND HANDLING ERROR")
				print("COMMAND HANDLING ERROR")
				print(e)
