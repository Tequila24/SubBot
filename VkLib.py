# -*- coding: utf-8 -*-
"""
@author: Fuego
"""
import random
import vk_api
import json
from pprint import pprint
from vk_api.bot_longpoll import VkBotLongPoll


'''	
class MyLongPoll(VkBotLongPoll):
	import vk_api
	api = None

	def set_api(self, new_api: vk_api.VkApi):
		self.api = new_api

	def send_error_message(self):
		self.api.method('messages.send', {'peer_id': '2000000004',
										  'message': "@fuego, script error detected",
										  'random_id': random.randrange(999999)})

	def listen(self):
		while True:
			try:
				for event in self.check():
					yield event
			except ConnectionError:
				self.send_error_message()
'''

class VkLib:

	from vk_api.bot_longpoll import VkBotEventType

	def __init__(self, token: str, group_id: int):
		self.vk = vk_api.VkApi(token=token)
		self.longpoll = VkBotLongPoll(self.vk, group_id)

	def reply(self, peer_id: int, message: str, disable_mention: bool = True):
		self.vk.method('messages.send', {'peer_id': peer_id,
										 'message': message,
										 'disable_mentions': 1 if disable_mention else 0,
										 'random_id': random.randrange(999999)})

# This is not working at all, server error #10
# but Ill leave that here just in case
	def reply_to_msg(self, peer_id: int, reply_to_id: int, message: str):
		self.vk.method('messages.send', {'peer_id': peer_id,
										 'message': message,
										 'reply_to': reply_to_id,
										 'random_id': random.randrange(999999)})

	def get_user_domain_by_id(self, user_id: int):
		reply = self.vk.method('users.get', {'user_ids': user_id,
											 'fields': 'domain'})
		json_reply = json.loads(json.dumps(reply))
		return json_reply[0]['domain']

	def get_user_id_by_domain(self, user_domain: str):
		reply = self.vk.method('users.get', {'user_ids': user_domain,
											 'fields': 'id'})
		json_reply = json.loads(json.dumps(reply))
		return json_reply[0]['id']

	def get_chat_members(self, peer_id: int, group_id: int):
		reply = self.vk.method('messages.getConversationMembers', {'peer_id': peer_id,
																   'count:': 200,
																   'group_id': group_id})
		json_reply = json.loads(json.dumps(reply))
		members_count = json_reply['count']

		members: dict = dict()
		for i in range(members_count):
			member_id = int(json_reply['items'][i]['member_id'])
			if member_id > 0:
				member_domain = self.get_user_domain_by_id(json_reply['items'][i]['member_id'])
				members[member_id] = str(member_domain)
		return members

	def get_chat_members_count(self, peer_id: int, group_id: int):
		reply = self.vk.method('messages.getConversationMembers', {'peer_id': peer_id,
																   'count:': 200,
																   'group_id': group_id})
		json_reply = json.loads(json.dumps(reply))
		real_members_count = 0  # do not count bot as member!
		members_count: int = int(json_reply['count'])
		for i in range(members_count):
			member_id = int(json_reply['items'][i]['member_id'])
			if member_id > 0:
				real_members_count += 1

		return real_members_count

	def get_chats(self):
		reply = self.vk.method('messages.getConversations')
		json_reply = json.loads(json.dumps(reply))
		chatCount = int(json_reply['count'])
		#        chats = json_reply['items']
		#        for chat in chats
		#            print[]
		pprint(json_reply)
