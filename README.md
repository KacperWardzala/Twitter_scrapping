# Twitter_scrapping

## Description
This program automates the process of extracting metadata from tweets provided as links in a CSV file. The workflow includes:

  - Validating tweet URLs.
  - Scraping tweet content and metadata (e.g., likes, comments, retweets) using Playwright.
  - Saving the results to a structured CSV file.
The program is fully automated, leveraging Playwright for web rendering and multithreading for faster processing.

## Requirements
Before running the program, make sure you have the following installed:

  - Python: Version 3.8 or higher.
  - Dependencies: Install the required Python libraries using the command below:

      pip install playwright tqdm

  - Playwright Setup: Install browser binaries with:

      playwright install
    
## Usage
### 1. Input CSV File
Prepare a CSV file containing a list of tweet links. Each row should include at least one link in the format:

https://x.com/username/status/tweet_id

### 2. Running the Script
Run the script by specifying the paths to the input CSV file, the cleaned links file, and the output CSV file. Example:

python script.py

### 3. Output
The program will create:
  - A file with valid tweet links (cleaned_links.txt).
  - A CSV file containing the scraped metadata (output.csv), including:
    - Text: The content of the tweet.
    - Username: The author's username.
    - Date: The date the tweet was created.
    - Comment Count: The number of comments on the tweet.
    - Like Count: The number of likes the tweet received.
    - Share Count: The number of retweets.

## File Structure
- script.py: The main script that performs link validation, scraping, and result saving.
- cleaned_links.txt: An intermediate file containing only valid tweet links.
- output.csv: The final output file containing the tweet metadata.

## Features
- Link Validation: Filters valid tweet URLs from the input.
- Multithreading: Speeds up the scraping process by processing multiple tweets concurrently.
- Error Handling: Logs errors for tweets that couldn't be scraped.

## Potential Issues
- Rate Limits: Excessive scraping may trigger rate limits on X (formerly Twitter).
- Captcha/Blocking: Some tweets may require additional handling due to captchas or account restrictions.
- Playwright Errors: Ensure that the browser binaries are properly installed if you encounter runtime issues.

## Acknowledgments
This program uses the following technologies:

  - Playwright for browser automation.
  - tqdm for progress visualization.

## License
This project is open-source and available under the MIT License.

Feel free to modify the details, especially regarding filenames and paths, to better match your project specifics!
