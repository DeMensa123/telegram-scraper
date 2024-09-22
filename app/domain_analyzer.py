import matplotlib.pyplot as plt
from app.mongo_client import collection
import re
import tldextract
from config import result_folder, result_md_file, result_png_file


def extract_urls_and_domains(text):
    """
    Extract URLs and domains from the given text using regex.

    Args:
        text (str): The message text to extract URLs from.

    Returns:
        tuple: A list of extracted URLs and a list of corresponding domains.
    """
    # url_regex = re.compile(
    #     r"(https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s\)\]\,\*\>\<\{\}\|\\\^?#]{2,}|"
    #     r"www\.[a-zA-Z0-9][a-zA-Z0-9-]+[a-zA-Z0-9]\.[^\s\)\]\,\*\>\<\{\}\|\\\^?#]{2,}|"
    #     r"https?:\/\/(?:www\.|(?!www))[a-zA-Z0-9]+\.[^\s\)\]\,\*\>\<\{\}\|\\\^?#]{2,}|"
    #     r"www\.[a-zA-Z0-9]+\.[^\s\)\]\,\*\>\<\{\}\|\\\^?#]{2,}|"
    #     r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,6})",
    #     re.IGNORECASE,
    # )

    url_regex = re.compile(
        r"(https?:\/\/(?:www\.)?[a-zA-Z0-9][a-zA-Z0-9-]*(?:\.[a-zA-Z0-9-]+)+[^\s\)\]\,\*\>\<\{\}\|\\\^?#]{2,}|"
        r"www\.[a-zA-Z0-9][a-zA-Z0-9-]*(?:\.[a-zA-Z0-9-]+)+[^\s\)\]\,\*\>\<\{\}\|\\\^?#]{2,}|"
        r"https?:\/\/(?:www\.)?[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,6})[^\s\)\]\,\*\>\<\{\}\|\\\^?#]{2,}|"
        r"www\.[a-zA-Z0-9-]+(?:\.[a-zA-Z]{2,})[^\s\)\]\,\*\>\<\{\}\|\\\^?#]{2,}|"
        r"(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,})",
        re.IGNORECASE,
    )

    urls = re.findall(url_regex, text)
    domains = [tldextract.extract(url.lower()).registered_domain for url in urls]

    return urls, domains


def analyze_top_domains():
    """
    Analyze the top 10 most mentioned domains from the MongoDB collection,
    save the results to a markdown file, and generate a bar chart.
    """

    # Groups by domains and counts occurrences
    pipeline = [
        {"$unwind": "$domains"},
        {"$group": {"_id": "$domains", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10},
    ]

    top_domains = list(collection.aggregate(pipeline))

    # Save the top 10 domains to a markdown file
    with open(result_folder + result_md_file, "w") as file:
        file.write("\n## Top 10 Most Mentioned Domains\n")
        file.write("| Domain | Mentions |\n")
        file.write("|--------|----------|\n")
        for domain in top_domains:
            file.write(f"| {domain['_id']} | {domain['count']} |\n")

    domains = [domain["_id"] for domain in top_domains]
    mentions = [domain["count"] for domain in top_domains]

    # Create the bar chart
    plt.figure(figsize=(10, 6))
    bars = plt.bar(domains, mentions, color="skyblue")
    plt.xticks(rotation=40, ha="right")
    plt.ylabel("Mentions")
    plt.xlabel("Domains")
    plt.title("Top 10 Domains Mentioned")

    # Add counts at the top of each bar
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
        )

    plt.tight_layout()
    plt.savefig(result_folder + result_png_file)
    plt.show()
