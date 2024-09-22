import logging
import asyncio
from telethon import TelegramClient, errors
from config import API_ID, API_HASH, PHONE, TELEGRAM_SESSION, BATCH_SIZE
from app.mongo_client import insert_or_update_message, setup_mongo_indexes
from app.utils import TelegramMessage
from app.domain_analyzer import extract_urls_and_domains
from app.mongo_client import collection


class TelegramScraper:
    def __init__(self):
        self.telegram_client = TelegramClient(TELEGRAM_SESSION, API_ID, API_HASH)

    async def connect(self):
        """Start the Telegram client and log in."""
        try:
            await self.telegram_client.start(phone=PHONE)
            logging.info(
                f"Connected to Telegram as {await self.telegram_client.get_me()}"
            )
        except Exception as e:
            logging.error(f"Error connecting to Telegram: {e}")

    async def process_message(self, message, channel):
        """
        Process each message by extracting URLs, domains, and saving to MongoDB.

        Args:
            message: The message object from Telegram.
            channel: the Telegram channel to scrape messages from.
        """

        try:
            if message.text:

                urls, domains = extract_urls_and_domains(message.text)
                logging.info(f"Message: {message.text}")
                logging.info(f"Extracted URLs: {urls}")
                logging.info(f"Extracted Domains: {domains}")

                message_data = TelegramMessage(
                    channel.title,
                    message,
                    urls,
                    [domain for domain in domains if domain != ""],
                ).to_dict()

            else:
                message_data = TelegramMessage(channel.title, message).to_dict()

            insert_or_update_message(message_data)

        except Exception as e:
            logging.error(f"Error processing message {message.id}: {e}")

    def get_last_processed_timestamp(self, channel):
        """
        Retrieve the last processed timestamp for the given channel.

        Args:
            channel: the Telegram channel to scrape messages from.
        """

        last_message = collection.find_one(
            {"channel_name": channel.title}, sort=[("timestamp", -1)]
        )

        return last_message["message_id"] if last_message else 0

    async def scrape_messages(self, channel_url):
        """
        Scrape messages in batches from the specified channel.

        Args:
            channel_url (str): The URL of the Telegram channel to scrape messages from.
        """

        while True:
            try:
                channel = await self.telegram_client.get_entity(channel_url)
                last_processed_id = self.get_last_processed_timestamp(channel)
                max_processed_id = 0  # Set to 0 for scraping the newest message

                while True:

                    messages = []
                    print("last_processed_id : ", last_processed_id)

                    # Retrieve messages newer than the last processed message
                    async for message in self.telegram_client.iter_messages(
                        channel,
                        min_id=last_processed_id,
                        max_id=max_processed_id,
                        limit=BATCH_SIZE,
                    ):

                        messages.append(message)
                        await self.process_message(message, channel)
                        max_processed_id = message.id

                        # async for comment_message in telegram_client.iter_messages(
                        #     channel, reply_to=message.id
                        # ):

                        #     print(comment_message.text)
                        #     await process_message(comment_message, channel)

                    logging.info(f"Processed a batch of {len(messages)} messages.")
                    if not messages:
                        break

                    await asyncio.sleep(2)

                setup_mongo_indexes()
                logging.info(
                    f"Finished scraping messages from {channel.title}: {channel_url}"
                )

                break

            # Handling Telegram API Rate Limits
            except errors.FloodWaitError as e:
                logging.warning(f"Rate limit hit. Sleeping for {e.seconds} seconds.")
                await asyncio.sleep(e.seconds)
                continue
            except Exception as e:
                logging.error(f"Error scraping messages from {channel_url}: {e}")
                logging.info("Retrying in 5 seconds...")
                await asyncio.sleep(5)
