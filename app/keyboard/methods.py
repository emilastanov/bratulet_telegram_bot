from telegram import InlineKeyboardMarkup

from bot.api import db_connector, get_chat_info, send_message_to
from constants import dialogs
from helpers.builders import build_menu, make_inline_buttons
from keyboard.keyboards import main_menu


def get_user_notifications(chat_id):
    collection = db_connector('cb_collector')
    subscriber = collection.find_one({"chat_id": chat_id})
    return subscriber['notifications']


def get_user_step(chat_id):
    collection = db_connector('cb_collector')
    subscriber = collection.find_one({"chat_id": chat_id})
    return subscriber['menu_step']


def change_user_step(chat_id, step):
    collection = db_connector('cb_collector')
    collection.find_one_and_update(
        {"chat_id": chat_id},
        {"$set": {"menu_step": step}}
    )


async def show_start_menu(update, _):
    chat_id, name = get_chat_info(update)

    menu, text = main_menu

    reply_markup = InlineKeyboardMarkup(
        build_menu(
            make_inline_buttons(menu),
            n_cols=2
        )
    )

    change_user_step(
        chat_id,
        {
            'current': 'main_menu',
            'previous': None
        }
    )

    await send_message_to(text, chat_id, keyboard=reply_markup)


async def show_turn_off_notifications_menu(chat_id):
    collection = db_connector('cb_collector')
    subscriber = collection.find_one({"chat_id": chat_id})

    notifications = subscriber['notifications']

    notifications = [
        [notification, f'off_notification_{notification}']
        for notification in notifications
    ]

    reply_markup = InlineKeyboardMarkup(
        build_menu(
            make_inline_buttons(notifications),
            n_cols=2
        )
    )

    change_user_step(
        chat_id,
        {
            'current': 'notifications',
            'previous': None
        }
    )

    await send_message_to(dialogs.turn_off_notification, chat_id, keyboard=reply_markup)
