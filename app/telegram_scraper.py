import logging
import asyncio
from telethon import TelegramClient, errors
from config import API_ID, API_HASH, PHONE, TELEGRAM_SESSION, BATCH_SIZE
from app.utils import TelegramMessage
from app.domain_analyzer import extract_urls_and_domains
from app.mongo_client import MongoClient


class TelegramScraper:
    def __init__(self, mongo_client: MongoClient):
        self.telegram_client = TelegramClient(TELEGRAM_SESSION, API_ID, API_HASH)
        self.mongo_client = mongo_client

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
            channel: The Telegram channel to scrape messages from.
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

            self.mongo_client.insert_or_update_message(message_data)

        except Exception as e:
            logging.error(f"Error processing message {message.id}: {e}")

    async def process_message_and_comments(self, message, channel):
        """
        Process a message and scrape its comments concurrently.

        Args:
            message: The Telegram message to process.
            channel: The Telegram to scrape messages from.
        """
        try:
            # Process the main message
            await self.process_message(message, channel)

            # Concurrently fetch and process the comments for the message
            comments = []
            if message.replies is not None and message.replies.replies > 0:

                async for comment_message in self.telegram_client.iter_messages(
                    channel, reply_to=message.id, limit=BATCH_SIZE
                ):
                    comments.append(comment_message)
                    await self.process_message(comment_message, channel)

            logging.info(f"Processed {len(comments)} comments for message {message.id}")

        except Exception as e:
            logging.error(f"Error processing message {message.id} or its comments: {e}")

    async def scrape_messages(self, channel_url: str):
        """
        Scrape messages in batches from the specified channel.

        Args:
            channel_url (str): The URL of the Telegram channel to scrape messages from.
        """

        while True:
            try:
                channel = await self.telegram_client.get_entity(channel_url)
                last_processed_id = self.mongo_client.get_last_processed_timestamp(
                    channel
                )
                max_processed_id = 0  # Set to 0 for scraping the newest message

                while True:

                    messages = []

                    # Retrieve messages newer than the last processed message
                    async for message in self.telegram_client.iter_messages(
                        channel,
                        min_id=last_processed_id,
                        max_id=max_processed_id,
                        limit=BATCH_SIZE,
                    ):

                        messages.append(message)
                        max_processed_id = message.id

                    logging.info(f"Processed a batch of {len(messages)} messages.")

                    if not messages:
                        break

                    await asyncio.gather(
                        *[
                            self.process_message_and_comments(message, channel)
                            for message in messages
                        ]
                    )

                    await asyncio.sleep(1)

                self.mongo_client.setup_mongo_indexes()
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
