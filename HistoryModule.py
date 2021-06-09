# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import VkLib
import SubDB
from datetime import datetime
from pprint import pprint

class HistoryModule:

	def __init__(self, new_db_handle: SubDB, new_vk_handle: VkLib):
		self.db_handle = new_db_handle
		self.vk_handle = new_vk_handle
		self.db_handle.create_table("messages_history", [	("message_id", "INTEGER"),
															("author_id", "INTEGER"),
															("date", "TEXT"),
															("text", "TEXT") ])

	def save_message(self, message_id: int, author_id: int, message_date: int, message_text: str):
		formatted_message_date: str = datetime.fromtimestamp(message_date).strftime("%Y-%m-%d %H:%M:%S")
		print(message_text)
		self.db_handle.exc("""INSERT INTO 'messages_history' VALUES((?), (?), (?), (?));""", (message_id, author_id, formatted_message_date, message_text))
		self.db_handle.com()
		#print("{0} {1}\n{2}\n{3}".format(message_id, author_id, formatted_message_date, message_text))

	def get_last_n_messages(self, messages_amount: int):
		query = """SELECT * FROM 'messages_history' WHERE message_id BETWEEN ((SELECT MAX(message_id) FROM 'messages_history') - {0}) AND (SELECT MAX(message_id) FROM 'messages_history');""".format(messages_amount)
		result = self.db_handle.exc(query)
		pprint(result)
