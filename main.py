from telethon import TelegramClient, sync
from telethon.tl.types import (
    MessageService,
    MessageMediaDocument,
    MessageActionPhoneCall,
)

import argparse
import os
from dotenv import load_dotenv

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--username", type=str, help="Имя пользователя для подсчета")
parser.add_argument("--test_mode", type=bool, default=False, help="Режим тестирования")
parser.add_argument(
    "--test_count", type=int, default=-1, help="Количество сообщений для просмотра"
)
args = parser.parse_args()

# Macros
TEST_MODE = args.test_mode
TEST_COUNT = args.test_count

username = args.username
if username == None:
    print("Не указано имя пользователя")
    exit(0)

api_id = os.getenv("API_ID")
api_hash = os.getenv("API_HASH")
client = TelegramClient("session_name", api_id, api_hash)
client.start()


# Our ids
user_id = -1
my_id = client.get_me().id

for dialog in client.iter_dialogs():
    if dialog.title == username:
        user_id = dialog.id
        if TEST_MODE:
            print(dialog.title, dialog.id)

if user_id == -1:
    print("Пользователь не найден")
    exit()


avarage_typing_speed_in_minute = 200.0
total_minutes_count = 0

for message in client.iter_messages(user_id):
    if TEST_MODE:
        TEST_COUNT -= 1
        if TEST_COUNT == 0:
            break
    # print(message.message, message.peer_id.user_id, my_id)
    if message.message != None:
        total_minutes_count += len(message.message) / avarage_typing_speed_in_minute

    # Rounds
    if (
        message.media
        and isinstance(message.media, MessageMediaDocument)
        and message.media.document != None
    ):
        if message.media.round == True:
            if TEST_MODE:
                print("Round: ", message.media.document.attributes[0].duration)
            # Took time twice
            total_minutes_count += (
                2.0 * message.media.document.attributes[0].duration / 60.0
            )

    # Calls
    if isinstance(message, MessageService) and isinstance(
        message.action, MessageActionPhoneCall
    ):
        if TEST_MODE:
            print("Call: ", message.action.duration)
        if message.action.duration != None:
            total_minutes_count += message.action.duration / 60.0

    # Voices
    if (
        isinstance(message.media, MessageMediaDocument)
        and message.media.voice == True
        and message.media.document != None
    ):
        if TEST_MODE:
            print("Voice: ", message.media.document.attributes[0].duration)
        # Took time twice
        total_minutes_count += (
            2.0 * message.media.document.attributes[0].duration / 60.0
        )

    # Voices
    if (
        isinstance(message.media, MessageMediaDocument)
        and message.media.video == True
        and message.media.document != None
    ):
        if TEST_MODE:
            print("Video: ", message.media.document.attributes[0].duration)
        total_minutes_count += message.media.document.attributes[0].duration / 60.0

print(
    "Всего {} провел времени с {} в Telegram {} часов и {} минут".format(
        client.get_me().first_name,
        username,
        int(total_minutes_count // 60),
        int(total_minutes_count) % 60,
    )
)
