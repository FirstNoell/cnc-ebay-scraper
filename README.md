# CNC eBay Scraper

A Scrapy + Selenium spider to scrape CNC machine listings from eBay. The spider extracts key details about each listing, including title, price, link, condition, shipping, location, offer type, and reviews.

## Features

- Scrapes CNC machine listings from eBay
- Captures up to 5 pages of search results
- Extracts the following fields:
  - `title`
  - `price`
  - `link`
  - `condition`
  - `shipping`
  - `location`
  - `offer_type`
  - `review_rating`
  - `review_count`
- Saves data to CSV (`cnc_machines.csv`)

## Requirements

- Python 3.9+
- Scrapy
- Selenium
- ChromeDriver (compatible with your Chrome version)

## Usage

1. Clone the repository:

git clone https://github.com/FirstNoell/cnc-ebay-scraper.git
cd cnc-ebay-scraper
Install dependencies:

pip install -r requirements.txt
Run the spider:

scrapy crawl cnc
The output will be saved as cnc_machines.csv.

License
This project is licensed under the MIT License.










