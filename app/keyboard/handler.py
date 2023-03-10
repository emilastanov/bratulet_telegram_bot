from telegram import InlineKeyboardMarkup

from bot.api import get_available_currency, send_message_to
from commands.actions import get_active_notifications, get_notifications, turn_off_notifications
from constants import dialogs
from helpers.builders import build_menu, make_inline_buttons
from keyboard import keyboards
from keyboard.keyboards import manipulate_buttons
from keyboard.methods import get_user_step, change_user_step, show_turn_off_notifications_menu, \
    get_user_notifications


async def push_button(update, context):

    query = update.callback_query
    variant = query.data
    chat_id = query.from_user.id

    current_step, previous_step = get_user_step(chat_id).values()

    await query.answer()

    if variant == 'show_active_notifications':
        notification_list = get_active_notifications(chat_id)

        if len(notification_list) == 0:

            reply_markup = InlineKeyboardMarkup(
                build_menu(
                    make_inline_buttons(manipulate_buttons),
                    n_cols=2
                )
            )

            change_user_step(chat_id, {
                "current": "active_notifications",
                "previous": current_step
            })

            await query.edit_message_text(
                text=dialogs.active_notifications_does_not_exist,
                reply_markup=reply_markup
            )
        else:
            await show_turn_off_notifications_menu(chat_id)

    elif variant == 'notification_settings':
        currencies = [
            [cur, f'currency_{cur}']
            for cur in get_available_currency()
        ]

        reply_markup = InlineKeyboardMarkup(
            build_menu(
                make_inline_buttons(currencies + manipulate_buttons),
                n_cols=1
            )
        )

        change_user_step(chat_id, {
            "current": "select_currency",
            "previous": current_step
        })

        await query.edit_message_text(
            text=dialogs.notification_settings_currencies,
            reply_markup=reply_markup
        )

    elif variant.split('_')[0] == 'currency':
        selected_currency = variant.split('_')[1]

        banks = [
            [bank, f'bank_{selected_currency}_{bank}']
            for bank in get_available_currency()[selected_currency]
        ]

        reply_markup = InlineKeyboardMarkup(
            build_menu(
                make_inline_buttons(banks + manipulate_buttons),
                n_cols=1
            )
        )

        change_user_step(chat_id, {
            "current": "notification_settings",
            "previous": current_step
        })

        await query.edit_message_text(
            text=dialogs.notification_settings_currencies,
            reply_markup=reply_markup
        )

    elif variant.split('_')[0] == 'bank':
        command, currency, bank = variant.split('_')

        change_user_step(chat_id, {
            "current": "select_bank",
            "previous": current_step
        })

        await get_notifications(f'{currency}_{bank}', chat_id, context)

    elif variant.split('_')[0] == 'off' and variant.split('_')[1] == 'notification':
        off, notification, currency, bank = variant.split('_')

        await turn_off_notifications(chat_id, f'{currency}_{bank}', context)

    elif variant == 'back':

        if previous_step in ['select_currency', 'select_bank']:
            previous_step = 'main_menu'

        try:
            previous_menu, text = getattr(keyboards, previous_step)
            reply_markup = InlineKeyboardMarkup(
                build_menu(
                    make_inline_buttons(previous_menu),
                    n_cols=2
                )
            )
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup
            )
            change_user_step(chat_id, {
                "current": previous_step,
                "previous": current_step
            })
        except AttributeError:
            await send_message_to('Something went wrong...', chat_id)

    elif variant == 'reactivate':
        notifications = get_user_notifications(chat_id)

        for notification in notifications:
            await get_notifications(notification, chat_id, context, reactivate=True)

        await query.edit_message_text(
            text=dialogs.notifications_reactivated
        )


    else:
        await query.edit_message_text(text=f"Выбранный вариант: {variant}")
