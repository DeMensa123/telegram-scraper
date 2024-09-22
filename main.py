import asyncio
import argparse
from app.telegram_scraper import TelegramScraper


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
    """Main function to connect to Telegram, scrape messages, and analyze domains."""
    scraper = TelegramScraper()
    await scraper.connect()
    await scraper.scrape_messages(channel_url)


if __name__ == "__main__":
    args = parse_arguments()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(args.channel))
