import asyncio
import argparse
from app.telegram_scraper import TelegramScraper
from app.mongo_client import MongoClient
from app.domain_analyzer import analyze_top_domains


def parse_arguments():
    parser = argparse.ArgumentParser(
        description="Scrape messages from a Telegram channel."
    )
    parser.add_argument(
        "--channel",
        type=str,
        required=True,
        help="The URL of the Telegram channel to scrape.",
    )
    return parser.parse_args()


async def main(channel_url):
    """
    Main function to connect to Telegram, scrape messages, and analyze domains.

    Args:
        channel_url (str): The URL of the Telegram channel to scrape messages from.
    """
    mongo_client = MongoClient()
    telegram_scraper = TelegramScraper(mongo_client)

    await telegram_scraper.connect()
    await telegram_scraper.scrape_messages(channel_url)
    analyze_top_domains(mongo_client.collection)


if __name__ == "__main__":
    args = parse_arguments()

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        asyncio.run(main(args.channel))
    except KeyboardInterrupt:
        pass
