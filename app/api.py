from pymongo import MongoClient
from time import time
from config import *
import telegram


def log(data):
    collection = db_connector('log')
    data['timestamp'] = int(time())
    collection.insert_one(data)


def db_connector(collection):
    client = MongoClient(MONGODB_URL)
    return client['cryptobot'][collection]


async def send_message_to(message, to):
    bot = telegram.Bot(BOT_TOKEN)
    async with bot:
        await bot.send_message(text=message, chat_id=to, parse_mode="HTML")

        log({
            'action': "send.message",
            'to': to,
            'body': message
        })

