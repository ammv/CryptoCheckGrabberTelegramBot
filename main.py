from typing import List

activate_this_file = "venv/scripts/activate_this.py"

exec(compile(open(activate_this_file, "rb").read(), activate_this_file, 'exec'), dict(__file__=activate_this_file))

import yaml
import logging
import winsound
import asyncio

import signal
import atexit

from logging.handlers import RotatingFileHandler

from telethon.sync import TelegramClient, events

from telegram_grabber_helper import TelegramGrabberHelper

from cheque_db import DatabaseManager, ChequeGiveawayRecord

from html_utils import HtmlUtils

KEYWORDS = ('giveaway', 'раздача', 'конкурс', 'чек', 'cheque', 'xrocket', 'фастовые', 'розыгрыш', 'airdrop', 'аирдроп')
KEYWORD_LINKS = ('t.me/cryptobot/app?startapp=', 't.me/xrocket?start=')

# Создание основного объекта логгера
logger = logging.getLogger('my_logger')
logger.setLevel(logging.DEBUG)
# Создание обработчика для записи в файл
file_handler = RotatingFileHandler('log_file.log', mode='a+', encoding='utf-8', maxBytes=5*1024*1024, backupCount=2, delay=0)
file_handler.setLevel(logging.DEBUG)
file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(file_formatter)
# Создание обработчика для вывода в консоль
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
# Добавление обработчиков к логгеру
logger.addHandler(file_handler)
logger.addHandler(console_handler)

with open("config.yml", encoding='utf-8') as f:
    config = yaml.load(f.read(), Loader=yaml.FullLoader)

# Замените значения ниже своими данными
api_id = config['TelegramApi']['api_id']
api_hash = config['TelegramApi']['api_hash']
phone_number = config['TelegramApi']['phone_number']
password = config['TelegramApi']['password']

client: TelegramClient = TelegramClient('session', api_id, api_hash, system_version="4.16.30-vxCUSTOM")
helper: TelegramGrabberHelper = TelegramGrabberHelper(client)
db_manager = DatabaseManager('cheque.db')

output_group_name = 'Чеки XRocket, Халява, Розыгрыши'
output_group_link = r'https://t.me/+VJPZuLJ312VjMjky'
output_group_entity = None

can_start = False

def handle_exit(*args):
    try:
        db_manager.close_connection()
        asyncio.create_task(client.disconnect())
        logger.info('Stopping program')
    except BaseException as ex:
        logger.critical('Error while stopping program', exc_info=True)

@client.on(events.NewMessage(chats=(output_group_entity), blacklist_chats=True, func=lambda ev: ev.is_group or ev.is_channel))
async def handle_new_post(event):
    if not can_start:
        return
    try:

        link_to_message = await helper.get_link_to_message(event.message)
        link_to_message = 'https://' + link_to_message

        text = event.message.text.lower()
        text = text.encode().decode('utf-8', 'ignore')

        if not helper.has_keyword_in_text(text, KEYWORDS):
            return

        links = helper.get_keyword_link(event.message, KEYWORD_LINKS)
        if len(links) == 0:
            return

        links = filter(lambda x: '=inv_' not in x, links)

        records: List[ChequeGiveawayRecord] = [
            ChequeGiveawayRecord(event.message.chat_id, helper.get_link_type(link), link) for link in links]

        records = list(filter(lambda record: db_manager.add_cheque_giveaway_record(record), records))

        if len(records) == 0:
            return

        logger.info(f'Событие из [{helper.get_event_sender_type(event)}] {(await helper.get_event_sender_name(event))}'
                    f' (id: {event.message.id}) содержит ключевые слова! [{link_to_message}]')

        links = [x.link for x in records]

        rockets = list(filter(lambda x:  'rocket' in x.lower(), links))
        cryptobot = list(filter(lambda x: 'cryptobot' in x.lower(), links))

        message = f'{HtmlUtils.bold("From")}: {link_to_message}\n\n'

        if len(rockets) > 0:
            message += f'🚀{HtmlUtils.bold("xRocket")} ({len(rockets)}):\n'
            message += f'\n'.join(f"{i}. {HtmlUtils.hyperlink('Link', k)}" for i, k in enumerate(rockets, start=1)) + '\n\n'

        if len(cryptobot) > 0:
            message += f'🤖{HtmlUtils.bold("CryptoBot")} ({len(cryptobot)}):\n'
            message += f'\n'.join(f"{i}. {HtmlUtils.hyperlink('Link', k)}" for i, k in enumerate(cryptobot, start=1))

        await client.send_message(output_group_entity, message, parse_mode='html', link_preview=False)

        winsound.PlaySound('audio/notify.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)

    except Exception as ex:
        logger.critical('Ошибка!', exc_info=True)
        winsound.PlaySound('audio/error.wav', winsound.SND_FILENAME | winsound.SND_ASYNC)
        

async def main():
    global output_group_entity, can_start

    winsound.PlaySound('audio/start.wav', winsound.SND_FILENAME)

    logger.info('Старт телеграм-клиента')
    await client.start(password=password)

    # Получить объект чата по имени
    logger.info(f'Поиск группы {output_group_name}')
    entity = await client.get_entity(output_group_link)
    # Проверить, что это канал или группа
    if entity.title == output_group_name:
        logger.info(f'Группа {output_group_name} найдена!')
        output_group_entity = entity
        logger.info(f'Запускаем мониторинг сообщений')
        can_start = True
        await client.run_until_disconnected()
        db_manager.close_connection()
    else:
        logger.critical(f'Группу {output_group_name} не удалось найти!')

atexit.register(handle_exit)
signal.signal(signal.SIGTERM, handle_exit)
signal.signal(signal.SIGINT, handle_exit)

with client:
    client.loop.run_until_complete(main())

