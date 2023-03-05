from api import db_connector


def get_active_notifications(chat_id):
    collection = db_connector('cb_collector')

    user = collection.find_one({'chat_id': chat_id})
    return user['notifications']