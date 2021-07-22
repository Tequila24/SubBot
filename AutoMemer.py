# -*- coding: utf-8 -*-
"""
@author: Fuego
"""

import random
from VkLib import VkLib

class AutoMemer:

    nalogi_images = [   'rsc/nalog_putin.jpg',
                        'rsc/nalog_trump.jpg']

    def __init__(self, vk_handle: VkLib):
        self.vk = vk_handle

    def check_message(self, peer_id: int, message_text: str):
        if ' налог' in message_text or ' лог' in message_text:
            self.reply_nalogi(peer_id) if (random.randint(0, 10) > 7) else 0

    def reply_nalogi(self, peer_id: int):
        #randomize reply
        image_path = self.nalogi_images[random.randint(0, len(self.nalogi_images)-1)]
        #upload image
        attachment: [str] = [self.vk.upload_pic_to_chat(peer_id, image_path),]
        #reply image
        self.vk.reply(peer_id, ' ', attachment)