from telegram.ext import Application, CommandHandler

from commander import start, help_command, get_notifications, turn_off_notifications
from config import BOT_TOKEN


def commands():
    print('Commandor has been started...')
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("get_notifications", get_notifications))
    application.add_handler(CommandHandler("turn_off_notifications", turn_off_notifications))
    application.run_polling()


if __name__ == '__main__':
    commands()
