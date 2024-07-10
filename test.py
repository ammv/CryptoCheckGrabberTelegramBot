import asyncio
import unittest

import yaml
from telethon.sync import TelegramClient, events, utils

from aiotestcase import AioTestCase
from telegram_grabber_helper import TelegramGrabberHelper

with open("config.yml", encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)

# Замените значения ниже своими данными
api_id = config['TelegramApi']['api_id']
api_hash = config['TelegramApi']['api_hash']
phone_number = config['TelegramApi']['phone_number']
password = config['TelegramApi']['password']

class MyTestCase(AioTestCase):
    async def setUp(self):
        self.client = TelegramClient('session', api_id, api_hash, system_version="4.16.30-vxCUSTOM")
        self.helper = TelegramGrabberHelper(self.client)

        self.keywords = ('giveaway', 'раздача', 'конкурс', 'чек', 'cheque', 'xrocket', 'фастовые', 'розыгрыш', 'airdrop', 'аирдроп')
        self.keyword_links = ('t.me/cryptobot/app?startapp=', 't.me/xrocket?start=')

        await self.client.start(password=password)

    async def tearDown(self):
        await self.client.disconnect()

    async def test_async_get_link_to_message_from_channel(self):
        # https://t.me/useless_contentt/103
        message = await self.client.get_messages('useless_contentt', ids=103)
        result = await self.helper.get_link_to_message(message)
        self.assertEqual(result, 't.me/useless_contentt/103')

    async def test_async_has_keyword_in_text(self):
        # https://t.me/TonyyCashh/167
        message = await self.client.get_messages('TonyyCashh', ids=167)

        text = message.text.lower()
        text = text.encode().decode('utf-8', 'ignore')

        print(text)

        result = self.helper.has_keyword_in_text(text, self.keywords)
        self.assertEqual(result, True)

    async def test_async_get_keyword_link_in_inline_button(self):
        # https://t.me/TonyyCashh/167
        # https://t.me/CryptoBot/app?startapp=giveaway-GVMda9765rzk0
        message = await self.client.get_messages('TonyyCashh', ids=167)

        text = message.text.lower()
        text = text.encode().decode('utf-8', 'ignore')

        result = self.helper.get_keyword_link(message, self.keyword_links)

        result = result

        self.assertEqual(result, 'https://t.me/CryptoBot/app?startapp=giveaway-GVMda9765rzk0')

    async def test_async_get_keyword_link_in_text(self):
        # https://t.me/TONcoinsFREE/2988
        message = await self.client.get_messages('TONcoinsFREE', ids=2988)

        text = message.text.lower()
        text = text.encode().decode('utf-8', 'ignore')

        result = self.helper.get_keyword_link(message, self.keyword_links)
        self.assertEqual(result, 'https://t.me/xrocket?start=mc_Oy5h07GqzXaOylO')

    async def test_async_get_keyword_link_in_text_in_group_message(self):
        # https://t.me/marioontonchat/33480
        message = await self.client.get_messages('marioontonchat', ids=33480)

        text = message.text.lower()
        text = text.encode().decode('utf-8', 'ignore')

        result = self.helper.get_keyword_link(message, self.keyword_links)
        self.assertEqual(result, 'https://t.me/xrocket?start=mci_dZzzKQD9jiaCBk8')

    async def test_async_get_keyword_link_in_inline_button_in_group_message(self):
        # https://t.me/TONcoinsFREE/33484
        message = await self.client.get_messages('marioontonchat', ids=33484)

        text = message.text.lower()
        text = text.encode().decode('utf-8', 'ignore')

        result = self.helper.get_keyword_link(message, self.keyword_links)
        self.assertEqual(result, 'https://t.me/xrocket?start=mc_6D7sL3EFKR4rgXe')

    async def test_async_check_message_if_good(self):
        message = await self.client.get_messages('marioontonchat', ids=33484)

        links = []

        link_to_message = await self.helper.get_link_to_message(message)

        text = message.text.lower()
        text = text.encode().decode('utf-8', 'ignore')

        if not self.helper.has_keyword_in_text(text, self.keywords):
            self.assertEqual(True, False)

        link = self.helper.get_keyword_link(message, self.keyword_links)
        if link is None or link in links:
            self.assertEqual(True, False)

        self.assertEqual(link, 'https://t.me/xrocket?start=mc_6D7sL3EFKR4rgXe')

if __name__ == "__main__":
    unittest.main()
