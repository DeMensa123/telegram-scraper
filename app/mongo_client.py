from pymongo import MongoClient as Mc
from pymongo.errors import (
    ServerSelectionTimeoutError,
    AutoReconnect,
    NetworkTimeout,
    ConnectionFailure,
)
from config import MONGO_URI, DB_NAME, COLLECTION_NAME
import logging


class MongoClient:
    def __init__(self):
        try:
            # Initialize MongoDB client and collection
            client = Mc(MONGO_URI)
            logging.info(f"Connected to MongoDB: {MONGO_URI}")

        except ConnectionFailure as e:
            logging.error(f"Could not connect to server: {e}")
            exit(0)

        self._collection = client[DB_NAME][COLLECTION_NAME]

    @property
    def collection(self):
        return self._collection

    def setup_mongo_indexes(self) -> None:
        """
        Ensure that necessary indexes are set up on the MongoDB collection.

        Raises:
            Exception: If any error occurs while creating the indexes.
        """
        try:
            self._collection.create_index("message_id", unique=True)
            self._collection.create_index("channel_name")
            self._collection.create_index("domains")
            self._collection.create_index("timestamp")
            logging.info("Indexes created successfully.")
        except Exception as e:
            logging.error(f"Error setting up indexes: {e}")

    def insert_or_update_message(self, message_data: dict) -> None:
        """
        Insert or update the message data in MongoDB.

        Args:
            message_data (dict): The message data to be inserted or updated.

        Raises:
            ServerSelectionTimeoutError: If there is an issue connecting to MongoDB.
            AutoReconnect: If MongoDB connection is lost and an automatic reconnection is attempted.
            NetworkTimeout: If there is a network timeout while interacting with MongoDB.
            Exception: If any other error occurs during the insert/update operation.
        """
        try:

            self._collection.update_one(
                {"message_id": message_data["message_id"]},
                {"$set": message_data},
                upsert=True,
            )
            logging.info(
                f"Message {message_data['message_id']} inserted or updated successfully. {self._collection.name}"
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

    def get_last_processed_timestamp(self, channel):
        """
        Retrieve the last processed timestamp for the given channel.

        Args:
            channel: the Telegram channel to scrape messages from.
        Returns:
            int: The message ID of the last processed message from the given channel.
                If no messages are found in the database, the function returns 0.
        """

        try:
            last_message = self._collection.find_one(
                {"channel_name": channel.title}, sort=[("timestamp", -1)]
            )

            return last_message["message_id"] if last_message else 0

        except Exception as e:
            logging.error(
                f"Error retrieving last processed timestamp for {channel.title}: {e}"
            )
            return 0
