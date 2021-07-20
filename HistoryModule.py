# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import VkLib
from SubDB import SubDB
from datetime import datetime


class HistoryModule:

	def __init__(self, new_vk_handle: VkLib):
		self.db_handle = SubDB("sub24_messages")
		self.vk_handle = new_vk_handle
		self.db_handle.create_table("messages", [	("message_id", "INTEGER"),
															("author_id", "INTEGER"),
															("date", "TEXT"),
															("text", "TEXT") ])

	def save_message(self, message_id: int, author_id: int, message_date: int, message_text: str):
		formatted_message_date: str = datetime.fromtimestamp(message_date).strftime("%Y-%m-%d %H:%M:%S")
		self.db_handle.exc("""INSERT INTO 'messages' VALUES((?), (?), (?), (?));""", (message_id, author_id, formatted_message_date, message_text))
		self.db_handle.com()
		#print("{0} {1}\n{2}\n{3}".format(message_id, author_id, formatted_message_date, message_text))

	def get_last_n_messages(self, peer_id: int, messages_amount: int):
		if messages_amount > 50:
			self.vk_handle.reply(peer_id, "Максимальное количество сообщений из истории - 50")
			return

		result = self.db_handle.exc("""SELECT * FROM 'messages' ORDER BY message_id DESC LIMIT (?);""", (messages_amount, ))
		if len(result):
			reply: str = ''
			result.reverse()
			for line in result:
				reply += "\n@id{0} {1} \n{2}\n".format(line[1], line[2], line[3])
			self.vk_handle.reply(peer_id, reply)
		else:
			print("История пуста!")
