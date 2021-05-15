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

    def get_logs_timer(self, peer_id):
        last_log_date: str = self.db_handle.get_parameter("LastLogDate")
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
        self.db_handle.set_parameter("LastLogDate", datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
        reply_message = "Таймер логов сброшен"
        self.vk_handle.reply(peer_id, reply_message)
