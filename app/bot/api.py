from pymongo import MongoClient
from bson.objectid import ObjectId
from time import time
from constants.config import *
import telegram


def log(data):
    collection = db_connector('log')
    data['timestamp'] = int(time())
    collection.insert_one(data)


def db_connector(collection, db='cryptobot'):
    client = MongoClient(MONGODB_URL)
    return client[db][collection]


async def send_message_to(message, to, keyboard=None):
    bot = telegram.Bot(BOT_TOKEN)

    message_params = {
        'text': message,
        'chat_id': to,
        'parse_mode': "HTML"
    }

    if keyboard:
        message_params['reply_markup'] = keyboard

    async with bot:
        await bot.send_message(**message_params)

        log({
            'action': "send.message",
            'to': to,
            'body': message
        })


def get_chat_info(update):
    chat = update['message']['chat']
    chat_id = chat['id']
    name = chat['first_name']

    return chat_id, name


def get_available_currency():
    collection = db_connector('currencies')
    currencies = collection.find_one({"_id": ObjectId('6402f4fd344934e438b28a12')})
    del currencies['_id']

    return currencies
