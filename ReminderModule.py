# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

from VkLib import VkLib
from SubDB import SubDB
import re
from datetime import datetime, timedelta
from pprint import pprint
import typing


class ReminderModule:

	def __init__(self, new_vk_handle: VkLib):
		self.dbase = SubDB("sub24_reminders")
		self.vk_handle = new_vk_handle
		self.dbase.create_table("reminders", [	("id", "INTEGER"),
												("expiration_date", "TEXT"),
												("author_id", "INTEGER"),
												("text", "TEXT"),
												("chat_id", "INTEGER") ])

	def parse_reminder_command(self, reminder_raw: str) -> typing.Tuple[str, str]:
		expiration_date: str = ""
		reminder_text: str = ""

		if 'через' in reminder_raw:
			match = re.search(r'напомни (?:мне )?((?!мне ).+) через (?:(\d+) час(?:ов?|а?) ?)?(?:(\d+) минуты*у* ?)?(?:(\d+) секунды*у* ?)?', reminder_raw)
			if match:
				reminder_text = match.group(1)
				expiration_date = (datetime.now() + timedelta(0,
															  int(match.group(4)) if match.group(4) is not None else 0,
															  0,
															  0,
															  int(match.group(3)) if match.group(3) is not None else 0,
															  int(match.group(2)) if match.group(2) is not None else 0,
															  0) ).strftime("%Y-%m-%d %H:%M:%S")
		else:
			match = re.search(r'напомни (?:мне )?((?!мне ).+) (\d{4})?-?(\d{1,2})-(\d{1,2}) ?(?:в )?(\d{1,2})?:?(\d{1,2})?:?(\d{1,2})?', reminder_raw)
			if match:
				reminder_text = match.group(1)
				expiration_date = "{0}-{1}-{2} {3}:{4}:{5}".format(	match.group(2) if match.group(2) is not None else datetime.now().year,
																	match.group(3) if match.group(3) is not None else datetime.now().month,
																	match.group(4) if match.group(4) is not None else datetime.now().day,
																	match.group(5) if match.group(5) is not None else 10,
																	match.group(6) if match.group(6) is not None else 0,
																	match.group(7) if match.group(7) is not None else 0 )
		return expiration_date, reminder_text

	def create_reminder(self, peer_id: int, author_id: int, reminder_raw: str):

		expiration_date, reminder_text = self.parse_reminder_command(reminder_raw)

		print(expiration_date, reminder_text)

		response = (self.dbase.exc("SELECT MAX(id) FROM reminders"))[0]
		if response[0] is not None:
			reminder_id = response[0]+1
		else:
			reminder_id = 1
		self.dbase.exc("""INSERT INTO 'reminders' VALUES((?), (?), (?), (?), (?));""", (reminder_id, expiration_date, author_id, reminder_text, peer_id))
		self.dbase.com()
		self.vk_handle.reply(peer_id, "Окей, записал")

	def remove_reminder(self, peer_id: int, author_id: int, reminder_id: int):
		response = self.dbase.exc("""SELECT * FROM 'reminders' WHERE id=(?);""", (reminder_id, ))
		print(response)
		if len(response):
			if int(response[0][2]) == author_id:
				self.dbase.exc("""DELETE FROM 'reminders' WHERE id=(?);""", (reminder_id, ))
				self.dbase.com()
				self.vk_handle.reply(peer_id, "Твоя напоминалка номер {0} удалена!".format(reminder_id))
			else:
				self.vk_handle.reply(peer_id, "Нельзя удалить чужую напоминалку!")
		else:
			self.vk_handle.reply(peer_id, "Напоминалка с таким номером не найдена!")

	def get_reminders_for_user(self, peer_id: int, author_id: int):
		response = self.dbase.exc("""SELECT * FROM 'reminders' WHERE author_id = (?) ORDER BY expiration_date ASC;""", (author_id, ))
		author_domain = self.vk_handle.get_user_domain_by_id(author_id)
		if len(response):
			reply: str = "@{0}, вот твои напоминалки: \r\n".format(author_domain)
			for line in response:
				reply += "# {0}, {1}, {2}\r\n".format(line[0], line[1], line[3])
			self.vk_handle.reply(peer_id, reply, False)
		else:
			self.vk_handle.reply(peer_id, "{0}, у тебя нет напоминалок!".format(author_domain))

	def check_active_reminders(self):
		response = self.dbase.exc("""SELECT * FROM 'reminders'""")
		if len(response):
			for line in response:
				t_delta: float = (datetime.strptime(line[1], "%Y-%m-%d %H:%M:%S") - datetime.now()).total_seconds()
				#print(t_delta, line[0], line[1], line[2], line[3], line[4])
				if t_delta < 0.0:
					message: str = "@{0}, напоминаю: {1}".format(self.vk_handle.get_user_domain_by_id(line[2]), line[3])
					self.vk_handle.reply(line[4], message, False)
					self.dbase.exc("""DELETE FROM 'reminders' WHERE id=(?);""", (line[0], ))
					self.dbase.com()
