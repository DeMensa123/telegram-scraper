import logging
from typing import List, Optional


class TelegramMessage:
    """
    A class to represent a Telegram message, storing relevant attributes
    such as message ID, text, timestamp, sender ID, chat ID, extracted URLs, and domains.
    """

    def __init__(
        self,
        channel,
        message,
        urls: Optional[List[str]] = None,
        domains: Optional[List[str]] = None,
    ) -> None:
        self.channel_name: str = channel
        self.message_id: int = message.id
        self.text: str = message.text
        self.timestamp: str = message.date.isoformat()
        self.sender_id: int = message.sender_id
        self.chat_id: int = message.chat_id
        self.urls: Optional[List[str]] = urls or []
        self.domains: Optional[List[str]] = domains or []

    def to_dict(self):
        return self.__dict__


# Setup logging configuration
logging.basicConfig(
    filename="scraper.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
