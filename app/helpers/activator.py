from telegram import InlineKeyboardMarkup

from bot.api import db_connector, send_message_to
from helpers.builders import build_menu, make_inline_buttons
from keyboard.keyboards import reactivate


async def reactive_subscriptions():
    print('Send messages about notification reactivation.')
    collection = db_connector('cb_collector')
    subscribers = collection.find()

    for subscriber in subscribers:
        notifications = subscriber['is_active'] and subscriber['notifications']
        if notifications:
            keyboard, text = reactivate

            reply_markup = InlineKeyboardMarkup(
                build_menu(
                    make_inline_buttons(keyboard),
                    n_cols=1
                )
            )

            await send_message_to(text, subscriber['chat_id'], keyboard=reply_markup)

    return True
