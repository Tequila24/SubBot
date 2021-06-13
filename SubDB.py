# -*- coding: utf-8 -*-
"""
Created on Mon May  3 16:49:24 2021

@author: Fuego
"""
import sqlite3


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

	def create_table(self, table_name: str, params: list[tuple[str, str]]):
		query_begin = """CREATE TABLE IF NOT EXISTS '{0}'(""".format(table_name)
		query_params = ""
		if len(params) > 0:
			query_params += """{0} {1} PRIMARY KEY""".format(params[0][0], params[0][1])
			for i in range(1, len(params)):
				query_params += ', '
				query_params += """{0} {1}""".format(params[i][0], params[i][1])
		query_end = ");"

		query_full = query_begin + query_params + query_end
		self.cursor.execute(query_full)
		self.db.commit()

	def exc(self, query: str, values: tuple = ()):
		self.cursor.execute(query, values)
		return self.cursor.fetchall()

	def com(self):
		self.db.commit()
