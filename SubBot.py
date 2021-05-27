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

creatorID = 19155229
confID = 2000000001
testConfID = 2000000004

dices = {1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤', 6: '⑥'}

class SubBot:

	def __init__(self):
		self.token, self.group_id = self.load_settings_from_file()

		self.VkLib = VkLib(self.token, self.group_id)

		self.dBase = SubDB("Sub24Conference")
		self.dBase.create_tables()

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
		return False, ''

	def reply_help(self, peer_id: int):
		message_text: str = "Список доступных команд:"
		message_text += "{0} - {1}\n".format("помощь", "вывести список доступных команд")
		message_text += "{0} - {1}\n".format("эхо", "повторить сообщение")
		message_text += "{0} - {1}\n".format("кости", "бросить пару игровых костей")
		message_text += "{0} - {1}\n".format("логи таймер", "показать время с последних логов")
		message_text += "{0} - {1}\n".format("логи сброс", "сбросить дату последних логов на текущую")
		message_text += "{0} - {1}\n".format("кто пидор", "показать пидора на сегодня")
		message_text += "{0} - {1}\n".format("топ пидоров", "показать таблицу лидеров-пидеров")
		self.VkLib.reply(peer_id, message_text)

	def echo(self, peer_id: int, message: str):
		self.VkLib.reply(peer_id, '>' + message.strip())

	def reply_with_dice(self, peer_id: int, author_id: int):
		dice1 = random.randrange(1, 6)
		dice2 = random.randrange(1, 6)
		reply_text = '@{0} {1} {2}'.format(self.VkLib.get_user_domain_by_id(author_id), dices[dice1], dices[dice2])
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

					if 'ты живой' in message_text:
						self.VkLib.reply(peer_id, "Да вроде нормально")

					if 'кости' in message_text:
						self.reply_with_dice(peer_id, author_id)

					if 'логи' in message_text:
						if 'таймер' in message_text:
							self.Logs.get_logs_timer(peer_id)
						if 'сброс' in message_text:
							self.Logs.reset_logs_timer(peer_id)

					if 'кто пидор' in message_text:
						self.Faggots.check_today_pidor(peer_id)

					if 'топ пидоров' in message_text:
						self.Faggots.show_pidor_stats(peer_id)

			except Exception as e:
				self.VkLib.reply(testConfID, "COMMAND HANDLING ERROR")
				print("COMMAND HANDLING ERROR")
				print(e)
