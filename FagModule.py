# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import VkLib
import SubDB
from datetime import datetime
import time
import random


preheat_lines = [	"Время пришло ( ͡° ͜ʖ ͡°)",
					"The time has come and so have I",
					"И не надоело вам?",
					"Нормальные люди спят в это время вообще-то",
					"♪ ~Вкалывают роботы, а не человек~ ♪",
					"Вскрываем ящик Пандоры...",
					"Я здесь что б жвачку жевать и пидоров назначать, а жвачка у меня кончилась"	]

nomination_lines = [	"Герой-пидор сегодняшнего дня @{0}",
					"Правом, данным мне свыше, объявляю пидором дня @{0}!",
					"Ну и пидор же ты, @{0}",
					"Кто это такой красивый у нас? @{0}!",
					"У нас во дворе за такое убивают, @{0}",
					"╰( ͡° ͜ʖ ͡° )つ──☆*:・ﾟ Вжух и ты пидор, @{0}!",
					"@{0}, представитель вида faggot vulgaris",
					"Отринь свою гетеросексуальность, @{0}!"	]

countLines = [		"Минуточку, надо посчитать...",
					"Так... этот один раз, тут два.. так падажжи ёмана",
					"А ВОТ ОНИ",
					"В э фильме снимались",
					"Они сделали свой выбор" ]


class FagModule:

	def __init__(self, new_db_handle: SubDB, new_vk_handle: VkLib, new_bot_group_id):
		random.seed(time.time())
		self.db_handle = new_db_handle
		self.vk_handle = new_vk_handle
		self.bot_group_id = new_bot_group_id
		self.db_handle.create_table("fags_scoreboard", [("user", "INT"),
														("count", "INT") ])
		self.db_handle.create_table("fags_params", [("parameter", "TEXT"),
													("value", "TEXT") ])
		self.db_handle.create_table("fags_players", [("user_id", "INT"),
														("user_nickname", "TEXT")])

	def get_param(self, param_name):
		query = """SELECT * FROM '{0}' WHERE parameter = '{1}';""".format("fags_params", param_name)
		db_response = self.db_handle.exc(query)
		param_name, value = db_response[0]
		return value

	def set_param(self, param_name: str, param_value: str):
		query = """INSERT OR REPLACE INTO '{0}' VALUES('{1}', '{2}');""".format("fags_params", param_name, param_value)
		self.db_handle.exc(query)
		self.db_handle.com()
		
	def get_all(self, table_name: str):
		query: str = """SELECT * FROM '{0}'""".format(table_name)
		db_response = self.db_handle.exc(query)
		return db_response

	def modify_fag_count_for(self, user: int, modify_by: int):
		query: str = """SELECT * FROM fags_scoreboard WHERE user='{0}';""".format(user)
		response = self.db_handle.exc(query)
		user_pidor_count: int
		if len(response) != 0:
			user_pidor_count = response[0][1] + modify_by
		else:
			return
		query: str = """INSERT OR REPLACE INTO fags_scoreboard VALUES('{0}', '{1}');""".format(user, user_pidor_count)
		self.db_handle.exc(query)
		self.db_handle.com()

	def check_today_fag(self, peer_id):
		# check if faggot was already chosen today
		last_fag_user_id: int = int(self.get_param("LastFagUser"))
		
		# check for cooldown
		last_fag_time: str = self.get_param("LastFagTime")
		if last_fag_time != 0:
			time_ago_in_secs: int = int((datetime.today() - datetime.strptime(last_fag_time, "%Y-%m-%d")).total_seconds())
			hours_ago: int = time_ago_in_secs // 3600
			if (hours_ago < 24) and (last_fag_user_id != -1):  # faggot was resetted manually
				time_left = 24 - hours_ago
				reply = "Если мне не изменяет память, пидор сегодня - {0}, и останется им ещё {1} часов".format(
					self.vk_handle.get_user_domain_by_id(last_fag_user_id),
					time_left)
				self.vk_handle.reply(peer_id, reply)
				return

		# we can not count members as usual anymore
		'''
		current_member_count: int = self.vk_handle.get_chat_members_count(peer_id, self.bot_group_id)
		players_list = self.get_all("fags_players")
		if current_member_count > len(players_list):
			self.vk_handle.reply(peer_id, "В списке пидоров кого-то не хватает!")
		elif current_member_count < len(players_list):
			self.vk_handle.reply(peer_id, "Кто-то вышел из чата, но остался в списке!")
		'''

		preheat_line = preheat_lines[random.randrange(0, len(preheat_lines))]
		self.vk_handle.reply(peer_id, preheat_line)
		time.sleep(1)

		players_list = self.get_all("fags_players")
		random.shuffle(players_list)
		today_fag = players_list[random.randrange(0, len(players_list))]
		self.modify_fag_count_for(today_fag[0], 1)
		self.set_param("LastFagTime", datetime.today().strftime("%Y-%m-%d"))
		self.set_param("LastFagUser", today_fag[0])

		nomination_line = nomination_lines[random.randrange(0, len(nomination_lines))]
		fag_reply = nomination_line.format(today_fag[1])
		self.vk_handle.reply(peer_id, fag_reply)

	def show_fag_stats(self, peer_id):
		reply: str = ''
		fags_list: dict = dict(self.get_all("fags_scoreboard"))
		if len(fags_list) == 0:
			reply = "А не было у нас ещё пидоров! Хаха!"
		else:
			fags_list = dict(sorted(fags_list.items(), key=lambda x: x[1], reverse=True))		# I like your funny words, magic lambda man
			print(fags_list)
			self.vk_handle.reply(peer_id, countLines[random.randrange(0, len(countLines))] )
			players_list = dict(self.get_all("fags_players"))
			for fag in fags_list.keys():
				fag_name: str
				if int(fag) in players_list.keys():
					fag_name = players_list[int(fag)]
				else:
					fag_name = self.vk_handle.get_user_domain_by_id(fag)
				reply += "{0} - {1} \r\n".format(fag_name, fags_list[fag])
		print(reply)
		self.vk_handle.reply(peer_id, reply)

	def reset_today_faggot(self, peer_id):
		last_fag_user_id: int = self.get_param("LastFagUser")
		if last_fag_user_id == 0:
			self.vk_handle.reply(peer_id, "Пидора ещё не выбирали!")
		else:
			self.set_param("LastFagUser", str(-1))
			self.modify_fag_count_for(last_fag_user_id, -1)
			self.vk_handle.reply(peer_id, "Пидор сброшен с Олимпа, счётчик снижен на 1")
