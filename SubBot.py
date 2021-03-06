# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import random
import json
from SubDB import SubDB
from VkLib import VkLib
from FagModule import FagModule
from LogModule import LogModule
from HistoryModule import HistoryModule
from ReminderModule import ReminderModule
from AutoMemer import AutoMemer
from pathlib import Path
from datetime import datetime
import traceback
import threading
import re

creatorID = 19155229
confID = 2000000001
testConfID = 2000000004

dices = {1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤', 6: '⑥'}


class SubBot(threading.Thread):

	def __init__(self):
		threading.Thread.__init__(self)
		self.token, self.group_id = self.load_settings_from_file()

		self.VkLib = VkLib(self.token, self.group_id)
		self.dBase = SubDB("sub24_conference")
		self.Faggots = FagModule(self.dBase, self.VkLib, self.group_id)
		self.Logs = LogModule(self.dBase, self.VkLib)
		self.history = HistoryModule(self.VkLib)
		self.reminderModule = ReminderModule(self.VkLib)
		self.automemer = AutoMemer(self.VkLib)

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
			match = re.match(r'((?:(?:бот)|(?:bot)|(?:sub24)|(?:суб24)),? ?)', message_text[:6].lower())
			if match:
				return True, message_text[len(match.group(1)):]
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
		архив последние N - показать последние N(1-50) сообщений из архива\n
		напомни (мне) %текст% через %часов %минут %секунд - Напоминалка с пингом! Например: "напомни попить чаю через 30 минут"
		другой формат - напомни (мне) %текст %год-%месяц-%день %час-%минута-%секунда. Если время не будет указано, напомнит в 10:00:00  \n
		мои напоминалки - вывести список ваших напоминалок\n
		удали напоминалку %n% - удалить напоминалку под номером N\n
		'''
		self.VkLib.reply(peer_id, message_text)

	def echo(self, peer_id: int, message: str):
		self.VkLib.reply(peer_id, '>' + message.strip())
				
	def reply_dice(self, peer_id: int, author_id: int, dices_amount, dice_value):
		if (dices_amount < 1) or (dice_value < 2):
			self.VkLib.reply(peer_id, "Количество костей должно быть больше 0, а значение - больше 1")
			return

		if (dices_amount > 999) or (dice_value > 999):
			self.VkLib.reply(peer_id, "превышен лимит")
			return

		reply_text = "@{0} ".format(self.VkLib.get_user_domain_by_id(author_id))		
		for i in range(dices_amount):
			reply_text += " " + str(random.randrange(1, dice_value+1))
		self.VkLib.reply(peer_id, reply_text)

	def scheduled_check(self):
		self.reminderModule.check_active_reminders()

	def run(self):
		while True:
			try:
				for event in self.VkLib.longpoll.listen():

					try:
						if event.type == VkLib.VkBotEventType.MESSAGE_NEW:

							json_event = json.loads(json.dumps(dict(event.object)))

							message_id = int(json_event['conversation_message_id'])
							author_id = int(json_event['from_id'])
							message_epoch_date = int(json_event['date'])
							peer_id = int(json_event['peer_id'])
							message_text = str(json_event['text']).strip()

							#pprint(json_event)
							if peer_id == confID:
								self.history.save_message(message_id, author_id, message_epoch_date, message_text)
							self.automemer.check_message(peer_id, message_text)

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
							if match:
								dices_amount = int(match.group(1))
								dice_value = int(match.group(2))
								self.reply_dice(peer_id, author_id, dices_amount, dice_value)

							if 'логи' in message_text:
								if 'таймер' in message_text:
									self.Logs.get_logs_timer(peer_id)
								if 'сброс' in message_text:
									self.Logs.reset_logs_timer(peer_id)

							if 'архив' in message_text:
								match = re.match(r'архив последние ([1-9][0-9]*)', message_text)
								if match:
									self.history.get_last_n_messages(peer_id, int(match.group(1)))

							if 'кто пидор' in message_text:
								self.Faggots.check_today_fag(peer_id)

							if 'топ пидоров' in message_text:
								self.Faggots.show_fag_stats(peer_id)

							if 'сброс пидора' in message_text:
								self.Faggots.reset_today_faggot(peer_id)

							match = re.search(r'напомни(?: мне)? (.+)', message_text)
							if match:
								self.reminderModule.create_reminder(peer_id, author_id, message_text)

							match = re.match(r'удали напоминалку (\d+)', message_text)
							if match:
								self.reminderModule.remove_reminder(peer_id, author_id, int(match.group(1)))

							if 'мои напоминалки' in message_text:
								self.reminderModule.get_reminders_for_user(peer_id, author_id)

							if 'упади' in message_text:
								self.VkLib.reply(peer_id, "падаю")
								exec(type((lambda: 0).__code__)(0, 1, 0, 0, 0, b'', (), (), (), '', '', 1, b''))

					except Exception as e:
						s: str = traceback.format_exc()
						self.VkLib.reply(testConfID, "COMMAND HANDLING ERROR: " + s)
						print("{0} FAIL".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
						traceback.print_exc()
						continue

			except Exception as e:
				print("VK FAILURE")
				print("{0} FAIL".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
				traceback.print_exc()
				continue
