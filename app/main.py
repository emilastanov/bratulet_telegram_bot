import asyncio
from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from helpers.activator import reactive_subscriptions
from keyboard.handler import push_button
from commands.commander import start, menu, off_notification
from constants.config import BOT_TOKEN


def commands():
    print('Commandor has been started...')

    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("off_notifications", off_notification))
    application.add_handler(CallbackQueryHandler(push_button))

    application.run_polling()


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(reactive_subscriptions())
    commands()
