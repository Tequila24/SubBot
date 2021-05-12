# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import random
import json
from pprint import pprint
from datetime import datetime
from SubDB import SubDB
from VkLib import VkLib
from pathlib import Path
import re
import time

creatorID = 19155229
confID = 2000000001
testConfID = 2000000004


def load_settings_from_file():
    token: str = "0"
    group_id: int = 0

    settings_file_path = Path('./settings.txt')
    if settings_file_path.is_file():
        file = open(settings_file_path, 'r')
        lines = file.readlines()
        for line in lines:
            if 'token=' in line:
                token = line[6:].strip()
            if 'group_id=' in line:
                group_id = int(line[9:].strip())
    print(token, group_id)
    return token, group_id


def check_is_for_me(message_text: str):
    if len(message_text) > 5:
        if 'sub24' in message_text[:5]:
            return True, message_text[5:]
        elif 'суб24' in message_text[:5]:
            return True, message_text[5:]
        elif 'бот' in message_text[:3]:
            return True, message_text[3:]
    return False, ''


class SubBot:

    def __init__(self):
        self.dices = {1: '①', 2: '②', 3: '③', 4: '④', 5: '⑤', 6: '⑥'}
        self.token, self.group_id = load_settings_from_file()

        self.VkLib = VkLib(self.token, self.group_id)

        self.dBase = SubDB("Sub24Conference")
        self.dBase.create_tables()

        self.dBase.set_parameter('test', 24)
        print(self.dBase.get_parameter('test'))
        print(self.dBase.get_parameter('test1'))

        #chat_members = self.VkLib.get_chat_members(confID, self.group_id)
        #for member_id in chat_members:
        #    self.dBase.add_user(member_id, chat_members[member_id])
        pprint(self.dBase.get_users_list())

        print('I am awake')

    def __exit__(self):
        print('bye')
        del self.dBase
        del self.VkLib

    def echo(self, peer_id: int, message: str):
        self.VkLib.reply(peer_id, 'echo: ' + message)

    def reply_with_dice(self, peer_id: int, author_id: int):
        dice1 = random.randrange(1, 6)
        dice2 = random.randrange(1, 6)
        reply_text = '@{0} {1} {2}'.format(self.VkLib.get_user_domain_by_id(author_id), self.dices[dice1], self.dices[dice2])
        self.VkLib.reply(peer_id, reply_text)

    def handle_logs(self, peer_id, author_id, message_text):
        if 'таймер' in message_text:
            last_log_date: str = self.dBase.get_parameter("LastLogDate")
            time_ago_in_secs: int = int((datetime.today() - datetime.strptime(last_log_date, "%Y-%m-%d %H:%M:%S")).total_seconds())
            hours_ago: int = time_ago_in_secs // 3600
            minutes_ago: int = (time_ago_in_secs - hours_ago * 3600) // 60
            seconds_ago: int = time_ago_in_secs - hours_ago * 3600 - minutes_ago * 60
            reply_message: str = "@{0} Последние логи были: {1}, {2} часов {3} минут {4} секунд назад".format(self.VkLib.get_user_domain_by_id(author_id),
                                                                                                              last_log_date,
                                                                                                              hours_ago,
                                                                                                              minutes_ago,
                                                                                                              seconds_ago)
            self.VkLib.reply(peer_id, reply_message)

        if 'сброс' in message_text:
            self.dBase.set_parameter("LastLogDate", datetime.today().strftime("%Y-%m-%d %H:%M:%S"))
            reply_message = "@{0} таймер логов сброшен".format(self.VkLib.get_user_domain_by_id(author_id))
            self.VkLib.reply(peer_id, reply_message)

    def check_today_pidor(self, peer_id):

        #check for cooldown
        last_pidor_time: str = self.dBase.get_parameter("LastPidorTime")
        if last_pidor_time != 0:
            time_ago_in_secs: int = int((datetime.today() - datetime.strptime(last_pidor_time, "%Y-%m-%d")).total_seconds())
            hours_ago: int = time_ago_in_secs // 3600
            if (hours_ago < 24):
                time_left = 24 - hours_ago
                last_pidor_user: str = self.dBase.get_parameter("LastPidorUser")
                reply = "Если мне не изменяет память, пидор сегодня - {0}, и останется им ещё {1} часов".format(last_pidor_user,
                                                                                                                time_left)
                self.VkLib.reply(peer_id, reply)
                return

        current_member_count: int = self.VkLib.get_chat_members_count(peer_id, self.group_id)
        members_list = self.dBase.get_users_list()
        if current_member_count > len(members_list):
            self.VkLib.reply(peer_id, "В списке пидоров кого-то не хватает!")
        elif current_member_count < len(members_list):
            self.VkLib.reply(peer_id, "Кто-то вышел из чата, но остался в списке!")
        time.sleep(1)
        self.VkLib.reply(peer_id, "А? Каво? Какой ещё пидор?")
        today_pidor = members_list[random.randrange(0, len(members_list))]
        self.dBase.add_pidor_to_base(today_pidor[1])
        self.dBase.set_parameter("LastPidorTime", datetime.today().strftime("%Y-%m-%d"))
        self.dBase.set_parameter("LastPidorUser", today_pidor[1])
        pidor_reply = "И сегодняшний пидор дня... @{0}! Поздравляем!".format(today_pidor[1])
        self.VkLib.reply(peer_id, pidor_reply)

    def show_pidor_stats(self, peer_id):
        reply: str = ''
        pidors_list = self.dBase.get_pidors_list()
        if len(pidors_list) == 0:
            reply = "А не было у нас ещё пидоров! Хаха!"
        else:
            reply = "Топ пидоров на сегодня:\r\n"
            for pidor in pidors_list:
                reply += "{0} - {1} \r\n".format(pidor[0], pidor[1])

        self.VkLib.reply(peer_id, reply)

    def run(self):

        for event in self.VkLib.longpoll.listen():
            try:
                print(event.type)
                if event.type == VkLib.VkBotEventType.MESSAGE_NEW:

                    json_event = json.loads(json.dumps(dict(event.object)))
                    author_id = int(json_event['from_id'])
                    peer_id = int(json_event['peer_id'])
                    message_text = str(json_event['text']).lower()

#                    if peer_id != testConfID:
#                        continue

                    is_for_me, message_text = check_is_for_me(message_text)
                    print(is_for_me, message_text)
                    if not is_for_me:
                        continue

                    if 'кости' in message_text:
                        self.reply_with_dice(peer_id, author_id)

                    if 'логи' in message_text:
                        self.handle_logs(peer_id, author_id, message_text)

                    if 'кто пидор' in message_text:
                        self.check_today_pidor(peer_id)

                    if 'топ пидоров' in message_text:
                        self.show_pidor_stats(peer_id)

                    #if 'добавь' in message_text and ''
            except:
                self.VkLib.reply(testConfID, "COMMAND HANDLING ERROR")
                print("COMMAND HANDLING ERROR")
