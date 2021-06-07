# -*- coding: utf-8 -*-
"""
@author: Fuego
"""


import SubBot
from datetime import datetime

if __name__ == "__main__":
	print('script working')
	bot = SubBot.SubBot()
	while True:
		try:
			bot.run()
		except Exception as e:
			print("{0} FAIL".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
			print(e)
			continue
