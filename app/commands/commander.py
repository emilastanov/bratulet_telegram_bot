from .actions import add_subscriber
from bot.api import send_message_to, get_chat_info
from constants import dialogs
from keyboard.methods import show_start_menu, show_turn_off_notifications_menu


async def start(update, context):
    await add_subscriber(*get_chat_info(update))
    await show_start_menu(update, context)


async def menu(update, context):
    await show_start_menu(update, context)


async def off_notification(update, _):
    chat_id, name = get_chat_info(update)
    await show_turn_off_notifications_menu(chat_id)


async def help_command(update, context):
    chat_id, name = get_chat_info(update)

    await send_message_to(dialogs.help_command, chat_id)
