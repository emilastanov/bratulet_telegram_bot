from telegram.ext import Application, CommandHandler, CallbackQueryHandler

from keyboard_handler import push_button
from commander import start, menu, off_notification
from config import BOT_TOKEN


def commands():
    print('Commandor has been started...')
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", menu))
    application.add_handler(CommandHandler("turn_off_notifications", off_notification))
    application.add_handler(CallbackQueryHandler(push_button))
    application.run_polling()


if __name__ == '__main__':
    commands()
