import unittest
from unittest.mock import AsyncMock, Mock, patch
from app.telegram_scraper import TelegramScraper
from config import PHONE


class TestTelegramScraper(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.scraper = TelegramScraper()

    @patch("app.telegram_scraper.TelegramClient")
    async def test_connect(self, mock_telegram_client):
        mock_instance = mock_telegram_client.return_value
        mock_instance.start = AsyncMock(return_value=None)
        mock_instance.get_me = AsyncMock(return_value="test_user")

        scraper = TelegramScraper()

        scraper.telegram_client = mock_instance

        await scraper.connect()

        mock_instance.start.assert_called_once_with(phone=PHONE)
        mock_instance.get_me.assert_called_once()

    @patch("app.telegram_scraper.extract_urls_and_domains")
    @patch("app.telegram_scraper.insert_or_update_message")
    async def test_process_message_with_text(self, mock_insert, mock_extract):
        mock_extract.return_value = (["http://example.com"], ["example.com"])
        message = Mock()
        message.text = "Check this out: http://example.com"

        channel = Mock()
        channel.title = "Test Channel"

        await self.scraper.process_message(message, channel)

        mock_extract.assert_called_once_with(message.text)
        mock_insert.assert_called_once()

    @patch("app.telegram_scraper.collection")
    def test_get_last_processed_timestamp(self, mock_collection):
        channel = Mock()
        channel.title = "Test Channel"
        mock_collection.find_one.return_value = {"message_id": 5}

        last_id = self.scraper.get_last_processed_timestamp(channel)

        mock_collection.find_one.assert_called_once()
        self.assertEqual(last_id, 5)


if __name__ == "__main__":
    unittest.main()
