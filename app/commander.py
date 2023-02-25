from telegram.ext import Application, CommandHandler

from api import send_message_to, db_connector, log
from config import BOT_TOKEN
import dialogs


async def add_subscriber(chat_id, name):
    collection = db_connector('cb_collector')

    is_exist = not not collection.find_one({'chat_id': chat_id})

    if not is_exist:
        collection.insert_one({
            "chat_id": chat_id,
            "is_active": True,
            "notifications": {
                "last_50_hours_average": True,
                "less_then": 0,
                "more_then": 0
            }
        })

        log({
            'action': "subscriber.added",
            'chat_id': chat_id
        })

        await send_message_to(dialogs.hello.format(name=name), chat_id)
    else:
        await send_message_to(dialogs.again.format(name=name), chat_id)


def get_chat_info(update):
    chat = update['message']['chat']
    chat_id = chat['id']
    name = chat['first_name']

    return chat_id, name


async def start(update, context):
    await add_subscriber(*get_chat_info(update))


async def help(update, context):
    chat_id, name = get_chat_info(update)

    await send_message_to(dialogs.help, chat_id)


def commands():
    print('Commandor has been started...')
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help))
    application.run_polling()


if __name__ == '__main__':
    commands()
