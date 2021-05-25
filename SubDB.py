# -*- coding: utf-8 -*-
"""
Created on Mon May  3 16:49:24 2021

@author: Fuego
"""
import sqlite3
import datetime


class SubDB:

	def __init__(self, db_name: str):
		self.db = None
		self.cursor = None
		self.isInit = False
		self.open_db(db_name)

	def __exit__(self, exc_type, exc_value, traceback):
		print('dbClosed')
		self.db.cursor.close()

	def open_db(self, db_name: str):
		self.db = sqlite3.connect(db_name + '.db')
		self.cursor = self.db.cursor()
		self.isInit = True

	def create_tables(self):
		# check if table with params exists
		query = """CREATE TABLE IF NOT EXISTS sub24_params(
					parameter TEXT PRIMARY KEY,
					value TEXT);"""
		self.cursor.execute(query)
		self.db.commit()

		# check if table with chat users
		query = """CREATE TABLE IF NOT EXISTS sub24_users(
						user_id INTEGER PRIMARY KEY,
						user_nickname TEXT);"""
		self.cursor.execute(query)
		self.db.commit()

		# check if table with pidor stats exists
		query = """CREATE TABLE IF NOT EXISTS sub24_pidors(
					user TEXT PRIMARY KEY,
					count INT);"""
		self.cursor.execute(query)
		self.db.commit()

	def add_user(self, user_id: int, user_nickname: str):
		query: str = """INSERT OR REPLACE INTO sub24_users VALUES('{0}', '{1}');""".format(user_id, user_nickname)
		self.cursor.execute(query)
		self.db.commit()

	def remove_user(self, user_id: int):
		query: str = """DELETE FROM sub24_users WHERE user_id='{0}';""".format(user_id)
		self.cursor.execute(query)
		self.db.commit()

	def get_users_list(self):
		query: str = """SELECT * from sub24_users;"""
		self.cursor.execute(query)
		users_list = self.cursor.fetchall()
		return users_list

	def add_pidor_to_base(self, user: str):
		query: str = """SELECT * FROM sub24_pidors WHERE user='{0}';""".format(user)
		self.cursor.execute(query)
		user_pidor_count = 0
		fetch = self.cursor.fetchone()
		if fetch is not None:
			if fetch[0] != 0:
				user_pidor_count = fetch[1] + 1
		else:
			user_pidor_count = 1
		print('PIDOR COUNT ' + str(user_pidor_count))
		query: str = """INSERT OR REPLACE INTO sub24_pidors VALUES('{0}', '{1}');""".format(user, user_pidor_count)
		self.cursor.execute(query)
		self.db.commit()

	def get_pidors_list(self):
		query: str = """SELECT * from sub24_pidors ORDER BY count;"""
		self.cursor.execute(query)
		pidors_list = self.cursor.fetchall()
		return pidors_list

	def set_parameter(self, param_name: str, param_value: str):
		query: str = """INSERT OR REPLACE INTO sub24_params VALUES('{0}', '{1}');""".format(param_name, param_value)
		self.cursor.execute(query)
		self.db.commit()

	def get_parameter(self, param_name: str):
		self.cursor.execute("""SELECT count(*) FROM sub24_params WHERE parameter = '{0}';""".format(param_name))
		if self.cursor.fetchone()[0] == 1:
			self.db.commit()
			query: str = """SELECT * from sub24_params WHERE parameter='{0}';""".format(param_name)
			self.cursor.execute(query)
			parameter, value = self.cursor.fetchone()
			return value
		else:
			return 0
