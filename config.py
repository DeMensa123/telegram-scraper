import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Telegram API credentials
API_ID = os.getenv("TELEGRAM_API_ID")
API_HASH = os.getenv("TELEGRAM_API_HASH")
PHONE = os.getenv("TELEGRAM_PHONE")
TELEGRAM_SESSION = os.getenv("TELEGRAM_SESSION")

# MongoDB connection details
MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")
COLLECTION_NAME = os.getenv("COLLECTION_NAME")

# Define batch size for scraping messages
BATCH_SIZE = 1000

# define output file names
result_folder = "results/"
result_md_file = "top_10_domains.md"
result_png_file = "top_10_domains.png"
