# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import VkLib
import SubDB
from datetime import datetime
import time
import random

class FagModule:

    def __init__(self, new_db_handle: SubDB, new_vk_handle: VkLib, new_bot_group_id):
        self.db_handle = new_db_handle
        self.vk_handle = new_vk_handle
        self.bot_group_id = new_bot_group_id

    def check_today_pidor(self, peer_id):
        # check for cooldown
        last_pidor_time: str = self.db_handle.get_parameter("LastPidorTime")
        if last_pidor_time != 0:
            time_ago_in_secs: int = int(
                (datetime.today() - datetime.strptime(last_pidor_time, "%Y-%m-%d")).total_seconds())
            hours_ago: int = time_ago_in_secs // 3600
            if (hours_ago < 24):
                time_left = 24 - hours_ago
                last_pidor_user: str = self.db_handle.get_parameter("LastPidorUser")
                reply = "Если мне не изменяет память, пидор сегодня - {0}, и останется им ещё {1} часов".format(
                    last_pidor_user,
                    time_left)
                self.vk_handle.reply(peer_id, reply)
                return

        current_member_count: int = self.vk_handle.get_chat_members_count(peer_id, self.bot_group_id)
        members_list = self.db_handle.get_users_list()
        if current_member_count > len(members_list):
            self.vk_handle.reply(peer_id, "В списке пидоров кого-то не хватает!")
        elif current_member_count < len(members_list):
            self.vk_handle.reply(peer_id, "Кто-то вышел из чата, но остался в списке!")
        time.sleep(1)
        self.vk_handle.reply(peer_id, "А? Каво? Какой ещё пидор?")
        today_pidor = members_list[random.randrange(0, len(members_list))]
        self.db_handle.add_pidor_to_base(today_pidor[1])
        self.db_handle.set_parameter("LastPidorTime", datetime.today().strftime("%Y-%m-%d"))
        self.db_handle.set_parameter("LastPidorUser", today_pidor[1])
        pidor_reply = "И сегодняшний пидор дня... @{0}! Поздравляем!".format(today_pidor[1])
        self.vk_handle.reply(peer_id, pidor_reply)

    def show_pidor_stats(self, peer_id):
        reply: str = ''
        pidors_list = self.db_handle.get_pidors_list()
        if len(pidors_list) == 0:
            reply = "А не было у нас ещё пидоров! Хаха!"
        else:
            reply = "Топ пидоров на сегодня:\r\n"
            for pidor in pidors_list:
                reply += "{0} - {1} \r\n".format(pidor[0], pidor[1])

        self.vk_handle.reply(peer_id, reply)