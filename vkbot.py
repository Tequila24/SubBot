# -*- coding: utf-8 -*-
"""
@author: Fuego
"""


import SubBot
from datetime import datetime
import time
import traceback
import threading

if __name__ == "__main__":
	print('script working')

	bot = SubBot.SubBot()
	bot.start()

	while True:
		try:
			time.sleep(1)
			bot.scheduled_check()
			
		except Exception as e:
			print("{0} FAIL".format(datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
			traceback.print_exc()
			continue

