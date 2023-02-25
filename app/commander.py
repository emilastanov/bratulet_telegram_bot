from api import send_message_to, db_connector, log
from listener import listener
import dialogs


async def add_subscriber(chat_id, name):
    collection = db_connector('cb_collector')

    is_exist = not not collection.find_one({'chat_id': chat_id})

    if not is_exist:
        collection.insert_one({
            "chat_id": chat_id,
            "is_active": True,
            "notifications": {
                "last_50_hours_average": False,
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


async def get_notifications(update, context):
    chat_id, name = get_chat_info(update)

    subscribers_collection = db_connector('cb_collector')
    subscriber = subscribers_collection.find_one({"chat_id": chat_id})

    is_already_active = subscriber['notifications']['last_50_hours_average']

    if is_already_active:
        await send_message_to(dialogs.already_received_this, chat_id)
    else:

        context.job_queue.run_repeating(lambda _c: listener(chat_id, _c), 120, chat_id=chat_id, name=str(chat_id))

        notifications = subscriber['notifications']
        notifications['last_50_hours_average'] = True

        subscribers_collection.find_one_and_update({"chat_id": chat_id},
                                                   {"$set": {"notifications": notifications}})

        await send_message_to(dialogs.get_last_50_average, chat_id)


async def turn_off_notifications(update, context):
    chat_id, name = get_chat_info(update)

    subscribers_collection = db_connector('cb_collector')
    subscriber = subscribers_collection.find_one({"chat_id": chat_id})

    notifications = subscriber['notifications']
    notifications['last_50_hours_average'] = False

    subscribers_collection.find_one_and_update({"chat_id": chat_id},
                                               {"$set": {"notifications": notifications}})

    job = context.job_queue.get_jobs_by_name(str(chat_id))
    job[0].schedule_removal()

    await send_message_to(dialogs.notification_terned_off, chat_id)


async def help_command(update, context):
    chat_id, name = get_chat_info(update)

    await send_message_to(dialogs.help_command, chat_id)
