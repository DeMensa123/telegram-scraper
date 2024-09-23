import unittest
from unittest.mock import AsyncMock, Mock, patch
from app.telegram_scraper import TelegramScraper
from config import PHONE
from app.mongo_client import MongoClient


class TestTelegramScraper(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.mongo_client = MongoClient()
        self.telegram_scraper = TelegramScraper(self.mongo_client)

    @patch("app.telegram_scraper.TelegramClient")
    async def test_connect(self, mock_telegram_client):

        mock_instance = mock_telegram_client.return_value
        mock_instance.start = AsyncMock(return_value=None)
        mock_instance.get_me = AsyncMock(return_value="test_user")

        self.telegram_scraper.telegram_client = mock_instance

        await self.telegram_scraper.connect()

        mock_instance.start.assert_called_once_with(phone=PHONE)
        mock_instance.get_me.assert_called_once()

    @patch("app.telegram_scraper.extract_urls_and_domains")
    @patch("app.telegram_scraper.MongoClient.insert_or_update_message")
    async def test_process_message_with_text(self, mock_insert, mock_extract):
        mock_extract.return_value = (["http://example.com"], ["example.com"])
        message = Mock()
        message.text = "Check this out: http://example.com"

        channel = Mock()
        channel.title = "Test Channel"

        await self.telegram_scraper.process_message(message, channel)

        mock_extract.assert_called_once_with(message.text)
        mock_insert.assert_called_once()


if __name__ == "__main__":
    unittest.main()
