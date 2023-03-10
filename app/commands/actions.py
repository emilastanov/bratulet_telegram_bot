from bot.api import send_message_to, db_connector, log
from commands.listener import listener
from constants import dialogs


async def add_subscriber(chat_id, name):
    collection = db_connector('cb_collector')

    is_exist = not not collection.find_one({'chat_id': chat_id})

    if not is_exist:
        collection.insert_one({
            "chat_id": chat_id,
            "name": name,
            "is_active": True,
            "notifications": {},
            "menu_step": {
                "current": 'main_menu',
                "previous": None
            }
        })

        log({
            'action': "subscriber.added",
            'chat_id': chat_id
        })

        await send_message_to(dialogs.hello.format(name=name), chat_id)
    else:
        await send_message_to(dialogs.again.format(name=name), chat_id)


async def get_notifications(currency_bank, chat_id, context, reactivate=False):

    subscribers_collection = db_connector('cb_collector')
    notifications = subscribers_collection.find_one({"chat_id": chat_id})['notifications']

    is_already_active = currency_bank in notifications

    if is_already_active and not reactivate:
        await send_message_to(dialogs.already_received_this, chat_id)
    else:

        context.job_queue.run_repeating(
            lambda _c: listener(chat_id, currency_bank, _c),
            120,
            chat_id=chat_id,
            name=f'{chat_id}_{currency_bank}'
        )

        notifications[currency_bank] = {
            'job_name': f'{chat_id}_{currency_bank}'
        }

        subscribers_collection.find_one_and_update({"chat_id": chat_id},
                                                   {"$set": {"notifications": notifications}})

        await send_message_to(dialogs.get_last_50_average, chat_id)


async def turn_off_notifications(chat_id, currency_bank, context):

    subscribers_collection = db_connector('cb_collector')
    subscriber = subscribers_collection.find_one({"chat_id": chat_id})

    notifications = subscriber['notifications']
    del notifications[currency_bank]

    subscribers_collection.find_one_and_update({"chat_id": chat_id},
                                               {"$set": {"notifications": notifications}})

    job = context.job_queue.get_jobs_by_name(f'{chat_id}_{currency_bank}')
    job[0].schedule_removal()

    await send_message_to(dialogs.notification_terned_off, chat_id)


def get_active_notifications(chat_id):
    collection = db_connector('cb_collector')

    user = collection.find_one({'chat_id': chat_id})
    return user['notifications']
