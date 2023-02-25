from time import sleep
import telegram
import asyncio

from api import db_connector, send_message_to, log
import dialogs


def get_list_of_subscriber():
    collection = db_connector('cb_collector')
    return collection.find()


def get_average_of_last_50_entities():
    collection = db_connector('offers')

    sum_of_last_10_entities = [
        entity['offers'][0]['price']
        for entity in collection.find(sort=[("timestamp", -1)])[:50]
    ]
    return sum(sum_of_last_10_entities)/len(sum_of_last_10_entities)


def get_last_currency_entity(chat_id):
    offers_collection = db_connector('offers')
    subscribers_collection = db_connector('cb_collector')

    entity = offers_collection.find_one(sort=[("timestamp", -1)])
    subscriber = subscribers_collection.find_one({"chat_id": chat_id})
    return entity['offers'][0], entity['_id'], subscriber.get('last_sent_offer_id')


def mark_entity_as_checked(mongo_id, chat_id):
    collection = db_connector('cb_collector')
    return collection.find_one_and_update({"chat_id": chat_id},
                                     {"$set": {"last_sent_offer_id": mongo_id}})


def change_subscriber_state(chat_id, state):
    collection = db_connector('cb_collector')
    current_state = collection.find_one({"chat_id": chat_id})['is_active']

    if current_state != state:
        log({
            'action': "subscriber.change_state",
            'chat_id': chat_id,
            'previous_state': current_state,
            'new_state': state
        })
        return collection.find_one_and_update({"chat_id": chat_id},
                                              {"$set": {"is_active": state}})


async def listener(chat_id, context):

    last_entity, mongo_id, last_sent_offer_id = get_last_currency_entity(chat_id)
    average_of_last_50_entities = get_average_of_last_50_entities()

    if (last_entity['price'] <= average_of_last_50_entities) and (mongo_id != last_sent_offer_id):
        await send_message_to(
            dialogs.last_50_hours_average.format(
                currency=last_entity['currency'],
                seller_stock=last_entity['seller_stock'],
                price=last_entity['price']
            ), chat_id)

        mark_entity_as_checked(mongo_id, chat_id)
