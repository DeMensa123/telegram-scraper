import logging
import asyncio
import argparse
from app.telegram_scraper import connect_to_telegram, scrape_messages, telegram_client
from domain_analyzer import analyze_top_domains

parser = argparse.ArgumentParser(description="Scrape messages from a Telegram channel.")
parser.add_argument(
    "--channel",
    type=str,
    required=True,
    help="The URL of the Telegram channel to scrape.",
)
args = parser.parse_args()


async def main(channel_url):
    """Main function to connect to Telegram, scrape messages, and analyze domains."""
    try:
        await connect_to_telegram()
        await scrape_messages(channel_url)
        analyze_top_domains()

    except Exception as e:
        logging.error(f"Error scraping messages: {e}")

    finally:
        await telegram_client.disconnect()


if __name__ == "__main__":
    loop = asyncio.get_event_loop()

    with telegram_client:
        loop.run_until_complete(main(args.channel))
