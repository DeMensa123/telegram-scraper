import logging
import os
from dotenv import load_dotenv
from telethon import TelegramClient
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, AutoReconnect, NetworkTimeout
import re
import tldextract
import asyncio

load_dotenv()

API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = "telegram_data"
COLLECTION_NAME = "messages"

logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]

telegram_client = TelegramClient("session_name", API_ID, API_HASH)


async def scrape_messages(channel_url):
    try:

        await telegram_client.start(phone=PHONE)
        logging.info(f"Connected to Telegram API as {await telegram_client.get_me()}")

        channel = await telegram_client.get_entity(channel_url)
        messages = []

        async for message in telegram_client.iter_messages(channel):
            messages.append(
                {
                    "message_id": message.id,
                    "text": message.text,
                    "timestamp": message.date,
                    "sender_id": message.sender_id,
                    "chat_id": message.chat_id,
                }
            )

        logging.info(f"Scraped {len(messages)} messages from {channel_url}")
        return messages

    except Exception as e:
        logging.error(f"Error scraping messages: {e}")
    finally:
        await telegram_client.disconnect()


def store_messages(messages):
    try:
        client.admin.command("ping")
        print("You successfully connected to MongoDB!")

        for message in messages:
            collection.update_one(
                {"message_id": message["message_id"]}, {"$set": message}, upsert=True
            )

        for message in collection.find():
            message_text = message.get("text", "")
            if message_text is not None:
                urls, domains = extract_urls_and_domains(message_text)

                collection.update_one(
                    {"_id": message["_id"]},
                    {
                        "$set": {
                            "urls": urls if urls else None,
                            "domains": domains if domains else None,
                        }
                    },
                )

        collection.create_index("message_id", unique=True)
        collection.create_index("timestamp")
        collection.create_index("domains")

        print("URLs and domains extracted and saved successfully.")

        logging.info(f"Successfully stored {len(messages)} messages in MongoDB")
    except ServerSelectionTimeoutError:
        logging.info("Failed to connect to MongoDB: Server selection timed out.")
    except AutoReconnect:
        logging.info("MongoDB server disconnected, attempting to reconnect.")
    except NetworkTimeout:
        logging.info("Network timeout while trying to connect to MongoDB.")


def extract_urls_and_domains(text):

    if text is None:
        return

    url_regex = re.compile(
        r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s\)\]]{2,}|www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s\)\]]{2,}|https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s\)\]]{2,}|www\.[a-zA-Z0-9]+\.[^\s\)\]]{2,})",
        re.IGNORECASE,
    )

    urls = re.findall(url_regex, text)

    if len(urls) > 0:
        logging.info(urls)

    domains = [tldextract.extract(url).registered_domain for url in urls]

    return urls, domains


if __name__ == "__main__":
    channel = "https://t.me/dannykollar"
    loop = asyncio.get_event_loop()
    messages = loop.run_until_complete(scrape_messages(channel))
    store_messages(messages)

    client.close()
