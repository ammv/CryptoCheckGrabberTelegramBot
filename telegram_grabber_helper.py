from telethon.tl.types import MessageEntityTextUrl

import re

from typing import List, Iterable, Set


class TelegramGrabberHelper:

    __REGEX_URL_PATTERN = re.compile('((www\.|http://|https://)(www\.)*.*?(?=(www\.|http://|https://|$)))')

    def __init__(self, client):
        self.__client = client

    def get_event_sender_type(self, event):
        if event.is_group:
            return 'Group'
        if event.is_channel:
            return 'Channel'
        return 'Неизвестно'

    async def get_event_sender_name(self, event):
        sender = await event.get_sender()
        if sender is None:
            return 'Неизвестно'
        return sender.username

    def has_keyword_in_text(self, text, keywords):
        for keyword in keywords:
            if keyword in text:
                return True
        return False

    def get_link_type(self, link):
        link = link.lower()

        if 'xrocket' in link:
            return 'x'
        if 'cryptobot' in link:
            return 'c'
        return '?'

    def get_keyword_link(self, message, keyword_links: Iterable[str]) -> Set[str]:
        links = set()
        for url_entity, inner_text in message.get_entities_text(MessageEntityTextUrl):
            for keyword_link in keyword_links:
                if keyword_link in url_entity.url:
                    links.add(url_entity.url)

        for keyword_link in keyword_links:
            for item in re.findall(TelegramGrabberHelper.__REGEX_URL_PATTERN, message.text):
                if keyword_link in item[0]:
                    links.add(item[0])

        if message.buttons is not None:
            for btn_row in message.buttons:
                for btn in btn_row:
                    url = btn.url
                    for keyword_link in keyword_links:
                        if keyword_link in url.lower():
                            links.add(url)

        return links

    async def get_link_to_message(self, message):
        chat = await self.__client.get_entity(message.chat_id)
        if chat.username is None:
            return f't.me/c/{chat.id}/{message.id}'
        return f't.me/{chat.username}/{message.id}'