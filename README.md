# Telegram Scraper with MongoDB Integration

## Overview
This project is a Python-based scraper for extracting messages from Telegram channels and storing them in MongoDB. It processes messages to extract URLs, their respective domains, and performs an analysis to present the top 10 most mentioned domains. The project is built using the [Telethon](https://pypi.org/project/Telethon/) library for interacting with the Telegram API and uses MongoDB for persistent storage.

## Features
- Telegram Channel Scraper: Extract messages from a Telegram channel.
- MongoDB Storage: Store Telegram messages, URLs, and domains in a MongoDB database.
- URL Extraction: Identify and extract URLs and domains from the messages.
- Top Domains Analysis: Analyze and visualize the top 10 most mentioned domains.
- Error Logging: Logs errors and activities to scraper.log for debugging.
- Resilient Async Handling: Gracefully handles asynchronous tasks using Python’s asyncio and Telethon.
- Batch Processing: Efficiently processes messages in batches, reducing the number of API calls and improving performance. The script retrieves messages incrementally based on the last processed message ID, ensuring that only new messages are scraped and stored to avoid duplicates.
- Asynchronous Programming: Asynchronous programming is utilized to handle multiple operations efficiently, especially when dealing with network requests and database interactions. Async and await are used to allow the program to handle multiple requests concurrently. When a message retrieval is initiated, the program can continue executing other tasks (e.g. processing previously retrieved messages) instead of waiting for the API response.



## Setup
1. Clone the repository:
    ```
    git clone https://github.com/yourusername/telegram-scraper
    cd telegram-scraper
    ```

2. Create a Conda environment:
   ```
    conda create --name telegram_scraper python=3.9
    conda activate telegram_scraper    
    ```

3. Install required packages:
    ```
    pip install -r requirements.txt
    ```


2. Environment variables:

    Create a .env file  with your Telegram API and MongoDB credentials according to .env.example file:
    ```
    TELEGRAM_API_ID=your_api_id
    TELEGRAM_API_HASH=your_api_hash
    TELEGRAM_PHONE=your_phone_number
    TELEGRAM_SESSION=your_telegram_session_name
    MONGO_URI=mongodb://localhost:27017/
    DB_NAME=your_database_name
    COLLECTION_NAME=your_collection_name
    ```



## Running the project
Once the environment is set up and all dependencies are installed, you can start scraping messages from a Telegram channel and storing them in MongoDB.

### Run the main script:

Run the script using the following command, replacing CHANNEL_URL with the URL of the Telegram channel you want to scrape:

```
python main.py --channel "CHANNEL_URL"
```

The scraper will:
- Connect to the Telegram channel specified by CHANNEL_URL.
- Process messages to extract URLs and domains.
- Store the message data, including URLs and domains, in MongoDB.
- Analyze and visualize the top 10 most mentioned domains.

## Output:
- MongoDB Storage: All messages, URLs, and domains will be stored in the specified MongoDB database and collection.
- Analysis: The top 10 domains by frequency will be saved as top_10_domains.png and also logged in a top_10_domains.md file in markdown format.

#### Top 10 Domains Markdown Report

The script ```domain_analyzes.py``` generates a **top_10_domains.md** file which includes the top 10 most mentioned domains from the scraped messages.

#### Top 10 Domains Chart

In addition to the markdown report, a bar chart (**top_10_domains.png**) is generated to visualize the mentions of the top 10 domains.



## Code Overview
The project is organized into multiple files, separating concerns between Telegram interaction, MongoDB handling, and utility functions.

### Project Structure

```bash
telegram-scraper/
│
├── .env.example                    # Environment variables example
├── config.py                       # Configuration file for loading environment variables
├── main.py                         # Main script to run the Telegram scraper
├── requirements.txt                # Python dependencies
├── README.md                   
├── telegram_data.messages.json     # Exported data from MongoDB               
├── app/
│   ├── __init__.py
│   ├── telegram_scraper.py         # Handles interaction with Telegram API
│   ├── domain_analyzer.py          # Analyzing top domains and generating visualizations
│   ├── mongo_client.py             # Handles MongoDB interactions and analysis
│   └── utils.py                    # Classes and logging setup
├── results/
│   ├── top_10_domains.md           # Markdown report showing top 10 domains
│   ├── top_10_domains.png          # Visualization of top 10 domains
├── tests/
│   ├── test_scraper.py             # Tests for Telegram and Mongo connections
│   ├── test_url.py                 # Tests for urls extraction
```


## MongoDB Schema
Each message in MongoDB has the following structure:
```
{
    "channel_name": <string>,       # Name of the Telegram channel from which the message was scraped.
    "message_id": <int>,            # Unique Telegram message ID
    "text": <string>,               # The message text
    "timestamp": <string>,          # ISO format timestamp of the message
    "sender_id": <int>,             # ID of the message sender
    "chat_id": <int>,               # ID of the Telegram chat (channel/group)
    "urls": [<list_of_urls>],       # List of extracted URLs
    "domains": [<list_of_domains>]  # List of extracted domains
}
```
Indexes are created on message_id,  channel_name and domains for faster querying and aggregation:
- message_id: This field is unique for each message, and an index on it allows for fast lookups and ensures no duplicates are stored.
- domains: An index on this field speeds up queries that analyze or filter messages by domain, enhancing performance for aggregations and lookups.
- channel_name: An index on this field significantly accelerates queries that retrieve all messages from a specific channel. As the application scales and more channels are scraped, this index maintains efficient query performance.
- timestamp: An index on this field speeds up queries based on message date and time. Indexing the timestamp field is also useful for finding the last processed message to scrape only new messages. 



## Error Handling & Logging
Errors during the message processing or MongoDB operations are logged to **scraper.log** file. The logging configuration is set to INFO level, and every step of the process is logged for easier debugging and monitoring.


## Schedulers

### Setting up scheduled execution on Windows

To ensure that the Telegram scraper runs periodically (e.g., daily) and processes only new messages, a scheduled task can be created using PowerShell. Follow these commands to configure it:

```
$Action = New-ScheduledTaskAction -Execute "c:\path\to\python.exe" -Argument "main.py --channel CHANNE_URL" -WorkingDirectory "C:\path\to\telegram-scraper"

$Trigger = New-ScheduledTaskTrigger -Daily -At "02:00AM"

$Principal = New-ScheduledTaskPrincipal -UserId "SYSTEM" -LogonType ServiceAccount

Register-ScheduledTask -Action $Action -Trigger $Trigger -Principal $Principal -TaskName "TelegramScraper" -Description "Scrapes messages from a Telegram channel daily."
```

### Steps to create a scheduled task using Task Scheduler

An alternative way to set up the Telegram scraper to run periodically is by using the Windows Task Scheduler GUI.

1. **Open Task Scheduler:** Start->Control Panel->System and Security->Administrative Tools->Task Scheduler

2. **Create a New Task:** In the right pane, click on "Create Basic Task..." and provide a name and description for the task (e.g., "Telegram Scraper"), then click "Next."

4. **Choose a Trigger and set the Start Time:** Select "Daily" and click "Next." Specify the start date and time for the task to run. Click "Next."

6. **Choose an Action:** Select "Start a program" and click "Next."

7. **Specify the Program/Script:**
    - Click "Browse" to navigate to the Python executable from virtual environment (e.g., `python.exe`).
    - In the "Add arguments (optional)" box, enter the path to the script, formatted as follows:
   
        ```
        "main.py --channel CHANNE_URL"
        ```
    - In the "Starts in (optional)" box, enter the path to the project, formatted as follows:

        ```
        "C:\path\to\telegram-scraper"
        ```

8. **Finish the Task Creation:** Click "Next," review the settings, and then click "Finish" to create the task.


By following these steps, automation of the Telegram scraper can be achieved, ensuring it runs daily and efficiently .processes new messages without duplicating data.

