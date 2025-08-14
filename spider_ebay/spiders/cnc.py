
import scrapy
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import re

class CncSpider(scrapy.Spider):
    name = "cnc"
    allowed_domains = ["ebay.com"]
    custom_settings = {
        "FEEDS": {
            "cnc_machines.csv": {
                "format": "csv",
                "fields": [
                    "title", "price", "link", "condition",
                    "shipping", "location", "offer_type",
                    "review_rating", "review_count"
                ],
                "overwrite": True,
            },
        },
        "LOG_LEVEL": "INFO",
        "DOWNLOAD_DELAY": 1,
    }

    max_pages = 25
    current_page = 1

    def start_requests(self):
        yield SeleniumRequest(
            url="https://www.ebay.com/sch/i.html?_nkw=cnc+machine&_sacat=0&_from=R40",
            callback=self.parse,
            wait_time=10,
            wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.s-item"))
        )

    def parse(self, response):
        items = response.css("li.s-item, li.s-item--large")
        self.logger.info(f"Page {self.current_page}: Found {len(items)} items.")

        for item in items:
            title_list = item.css(".s-item__title span::text").getall()
            title = " ".join([t.strip() for t in title_list if t.strip()]) or "N/A"
            if "Shop on eBay" in title:
                continue

            price = item.css(".s-item__price::text").get(default="N/A").strip()
            link = item.css(".s-item__link::attr(href)").get(default="N/A").strip()
            condition = item.css(".SECONDARY_INFO::text").get(default="N/A").strip()

            # Normalize shipping
            shipping_text = item.css(".s-item__shipping::text").get(default="0").strip()
            if "not specified" in shipping_text.lower():
                shipping = 0
            else:
                shipping_match = re.search(r"[\d,.]+", shipping_text)
                shipping = float(shipping_match.group().replace(",", "")) if shipping_match else 0

            location = item.css(".s-item__location.s-item__itemLocation::text").get(default="N/A").strip()

            # Offer type
            offer_type_list = []
            if item.css(".s-item__subtitle .s-item__subtitle-text::text").get():
                offer_type_list.append(item.css(".s-item__subtitle .s-item__subtitle-text::text").get().strip())
            if item.css(".s-item__purchase-options-with-icon::text").get():
                offer_type_list.append(item.css(".s-item__purchase-options-with-icon::text").get().strip())
            if item.css(".s-item__dynamic.s-item__formatBestOfferEnabled::text").get():
                offer_type_list.append(item.css(".s-item__dynamic.s-item__formatBestOfferEnabled::text").get().strip())
            if not offer_type_list:
                offer_type_list = ["N/A"]

            # Reviews
            review_rating_text = item.css(".s-item__reviews .x-star-rating .clipped::text").re_first(r"([\d.]+) out of 5 stars")
            review_rating = float(review_rating_text) if review_rating_text else 0

            review_count_text = item.css(".s-item__reviews-count span[aria-hidden='false']::text").re_first(r"(\d+)")
            review_count = int(review_count_text) if review_count_text else 0

            yield {
                "title": title,
                "price": price,
                "link": link,
                "condition": condition,
                "shipping": shipping,
                "location": location,
                "offer_type": ", ".join(offer_type_list),
                "review_rating": review_rating,
                "review_count": review_count,
            }

        # Pagination
        if self.current_page < self.max_pages:
            next_page = response.css("a.pagination__next::attr(href)").get()
            if next_page:
                self.current_page += 1
                yield SeleniumRequest(
                    url=next_page,
                    callback=self.parse,
                    wait_time=10,
                    wait_until=EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.s-item"))
                )
        else:
            self.logger.info(f"Reached max_pages ({self.max_pages}), stopping pagination.")
