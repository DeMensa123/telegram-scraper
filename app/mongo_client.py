from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect, NetworkTimeout
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
import logging


# Initialize MongoDB client and collection
client = MongoClient("mongodb://localhost:27017/")
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


def setup_mongo_indexes():
    """Ensure indexes are set up on the MongoDB collection."""
    try:
        collection.create_index("message_id", unique=True)
        collection.create_index("channel_name")
        collection.create_index("domains")
        collection.create_index("timestamp")
        logging.info("Indexes created successfully.")
    except Exception as e:
        logging.error(f"Error setting up indexes: {e}")


def insert_or_update_message(message_data):
    """
    Insert or update the message data in MongoDB.

    Args:
        message_data (dict): The message data to be inserted or updated.

    Raises:
        ServerSelectionTimeoutError: If there is an issue connecting to MongoDB.
    """
    try:
        collection.update_one(
            {"message_id": message_data["message_id"]},
            {"$set": message_data},
            upsert=True,
        )
        logging.info(
            f"Message {message_data['message_id']} inserted or updated successfully. {collection.name}"
        )
    except ServerSelectionTimeoutError as e:
        logging.error(f"Error connecting to MongoDB: {e}")
    except AutoReconnect:
        logging.info("MongoDB server disconnected, attempting to reconnect.")
    except NetworkTimeout:
        logging.info("Network timeout while trying to connect to MongoDB.")
    except Exception as e:
        logging.error(
            f"Error inserting/updating message {message_data['message_id']}: {e}"
        )
