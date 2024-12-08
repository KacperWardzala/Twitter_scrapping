"""
This script scrapes metadata from tweets using their URLs and saves the results to a CSV file.

Author: Kacper Wardzala
Date: 10.11.2024
License: MIT
"""

import re
from playwright.sync_api import sync_playwright
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm

# ======================================================
# Files operations (I/O)
# ======================================================

def extract_valid_links(input_csv: str, output_csv: str) -> None:
    """
    Extracts valid tweet URLs from an input CSV and writes them to an output file.

    Args:
        input_csv (str): Path to the input CSV file containing potential tweet URLs.
        output_csv (str): Path to the output file where valid links will be saved.
    """
    # Regex pattern to match valid tweet URLs
    regex = re.compile(r'https://x\.com/\w+/status/\d+$')

    # Open input and output files
    with open(input_csv, mode='r', newline='', encoding='utf-8') as infile, \
            open(output_csv, mode='w', newline='', encoding='utf-8') as outfile:

        csv_reader = csv.reader(infile)
        csv_writer = csv.writer(outfile)

        for row in csv_reader:
            for link in row:
                if regex.match(link):  # Check if the link matches the regex
                    csv_writer.writerow([link])  # Write valid link to the output file

# ======================================================
# Scraping
# ======================================================

def extract_username_from_url(url: str) -> str:
    """
    Extract the username from the tweet URL.

    Args:
        url (str): The tweet URL.

    Returns:
        str: The username extracted from the URL, or 'N/A' if not found.
    """
    match = re.search(r'https://x\.com/(\w+)/status/\d+', url)
    return match.group(1) if match else "N/A"  # Return the username if found


def scrape_tweet_metadata(url: str) -> dict:
    """
    Scrape a tweet page and return a dictionary with the tweet text and metadata.

    Args:
        url (str): The tweet URL to scrape.

    Returns:
        dict: A dictionary containing tweet metadata such as text, username, date,
              and engagement statistics.
    """
    _xhr_calls = []  # List to store intercepted XHR responses
    username = extract_username_from_url(url)  # Extract username from URL

    def intercept_response(response):
        """
        Capture all background XHR requests and save those that match tweet data.
        """
        if response.request.resource_type == "xhr":
            _xhr_calls.append(response)

    with sync_playwright() as pw:
        # Launch a browser in headless mode
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        # Attach the response interceptor to capture XHR requests
        page.on("response", intercept_response)

        # Navigate to the tweet URL
        page.goto(url)
        page.wait_for_selector("[data-testid='tweet']")  # Wait for the tweet to load

        # Filter XHR responses for tweet data
        tweet_calls = [f for f in _xhr_calls if "TweetResultByRestId" in f.url]

        # Extract metadata from the XHR responses
        for xhr in tweet_calls:
            data = xhr.json()
            result = data['data']['tweetResult']['result']['legacy']

            tweet_metadata = {
                "text": result.get('full_text', 'N/A'),
                "username": username,
                "date": result.get('created_at', 'N/A'),
                "comment_count": result.get('reply_count', 'N/A'),
                "like_count": result.get('favorite_count', 'N/A'),
                "share_count": result.get('retweet_count', 'N/A')
            }
            return tweet_metadata

        # Return default values if no data is found
        return {
            "text": "N/A",
            "username": username,
            "date": "N/A",
            "comment_count": "N/A",
            "like_count": "N/A",
            "share_count": "N/A"
        }


def get_links_from_csv(file_path: str) -> list:
    """
    Load links from a CSV file and return them as a list.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        list: A list of links found in the CSV file.
    """
    links = []
    with open(file_path, mode='r', newline='', encoding='utf-8') as infile:
        csv_reader = csv.reader(infile)
        for row in csv_reader:
            links.extend(row)  # Add all links from the row to the list
    return links


def save_results_to_csv(results: list, output_file: str) -> None:
    """
    Save results to a CSV file with columns: link; text; username; date; comment_count; like_count; share_count.

    Args:
        results (list): A list of tuples containing the link and its metadata.
        output_file (str): Path to the output CSV file.
    """
    with open(output_file, mode='w', newline='', encoding='utf-8') as outfile:
        csv_writer = csv.writer(outfile, delimiter=';')
        # Write the header row
        csv_writer.writerow(['Link', 'Text', 'Username', 'Date', 'Comment Count', 'Like Count', 'Share Count'])
        for link, metadata in results:
            # Write each result to the CSV file
            csv_writer.writerow([
                link,
                metadata.get('text', 'N/A'),
                metadata.get('username', 'N/A'),
                metadata.get('date', 'N/A'),
                metadata.get('comment_count', 'N/A'),
                metadata.get('like_count', 'N/A'),
                metadata.get('share_count', 'N/A')
            ])

# ======================================================
# Main
# ======================================================

def scrape_all_tweets(links: list) -> list:
    """
    Scrape metadata for a list of tweet links concurrently.

    Args:
        links (list): A list of tweet URLs to scrape.

    Returns:
        list: A list of tuples where each tuple contains a link and its metadata.
    """
    results = []
    with ThreadPoolExecutor(max_workers=5) as executor:
        # Submit scraping tasks to the thread pool
        future_to_link = {executor.submit(scrape_tweet_metadata, link): link for link in links}

        # Use tqdm for progress tracking
        with tqdm(total=len(links), desc="Scraping Tweets") as pbar:
            for future in as_completed(future_to_link):
                link = future_to_link[future]
                try:
                    # Get the result of the scraping task
                    metadata = future.result()
                    results.append((link, metadata if metadata else {"error": "Could not scrape"}))
                except Exception as e:
                    # Log errors encountered during scraping
                    results.append((link, {"error": f"Error: {e}"}))
                pbar.update(1)

    return results


if __name__ == "__main__":
    # Define paths
    input_csv = r"C:\Users\kacwa\Downloads\romantyzujcie.csv"
    output_csv = r"cleaned_links.txt"

    # Extract valid links from the input CSV file
    extract_valid_links(input_csv, output_csv)

    # Load links from the cleaned file
    links = get_links_from_csv(output_csv)

    # Scrape tweet metadata
    results = scrape_all_tweets(links)

    # Save the results to an output CSV file
    output_csv = r"romantyzujcie_meta.csv"
    save_results_to_csv(results, output_csv)
