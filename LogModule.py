# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import VkLib
import SubDB
from datetime import datetime


class LogModule:

	def __init__(self, new_db_handle: SubDB, new_vk_handle: VkLib):
		self.db_handle = new_db_handle
		self.vk_handle = new_vk_handle
		self.db_handle.create_table("logs_params", [	("parameter", "TEXT"),
														("value", "TEXT") ])

	def get_param(self, param_name):
		query = """SELECT * FROM '{0}' WHERE parameter = '{1}';""".format("logs_params", param_name)
		db_response = self.db_handle.exc(query)
		param_name, value = db_response[0]
		return value

	def set_param(self, param_name: str, param_value: str):
		query = """INSERT OR REPLACE INTO '{0}' VALUES('{1}', '{2}');""".format("logs_params", param_name, param_value)
		self.db_handle.exc(query)
		self.db_handle.com()

	def get_logs_timer(self, peer_id):
		last_log_date: str = self.get_param("LastLogDate")
		time_ago_in_secs: int = int((datetime.today() - datetime.strptime(last_log_date, "%Y-%m-%d %H:%M:%S")).total_seconds())
		hours_ago: int = time_ago_in_secs // 3600
		minutes_ago: int = (time_ago_in_secs - hours_ago * 3600) // 60
		seconds_ago: int = time_ago_in_secs - hours_ago * 3600 - minutes_ago * 60
		reply_message: str = "Последние логи были: {0}, {1} часов {2} минут {3} секунд назад".format(last_log_date,
																									 hours_ago,
																									 minutes_ago,
																									 seconds_ago)
		self.vk_handle.reply(peer_id, reply_message)

	def reset_logs_timer(self, peer_id):
		self.get_logs_timer(peer_id)
		self.set_param("LastLogDate", datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
		reply_message = "Таймер логов сброшен"
		self.vk_handle.reply(peer_id, reply_message)
