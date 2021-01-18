import os
import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import logging

# logging.INFO = log only info and above (no debug)
# logging.WARNING = log only warnings and above (no debug or info)
logging.basicConfig(
    level=logging.INFO,
    filename="application.log",
    format="%(asctime)s: %(levelname)s: %(message)s",
)


def log_warning(e, msg):
    logging.warning(msg)
    logging.warning(e)


def check_for_cookie_banner():
    try:
        if driver.find_element_by_id("closeCookieBanner").is_displayed():
            driver.find_element_by_id("closeCookieBanner").click()
            logging.info("Closed Cookie Banner")
        else:
            logging.info("Cookie banner not present, nothing to close.")
    except:
        e = sys.exc_info()
        logging.warning("Failed to close cookie banner")
        logging.warning(e)


def get_page_items():
    try:
        item_list = driver.find_elements_by_css_selector("div.thumbnail")
        logging.debug(f"Found item_list")
        return item_list
    except:
        e = sys.exc_info()
        logging.warning("Failed to find item_list")
        logging.warning(e)
        pass


# Get all items, prices and number of reviews on first 5 pages.
target_url = "https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops"
webdriver_path = os.path.abspath("chromedriver_win32\chromedriver.exe")
driver = webdriver.Chrome(webdriver_path)
action = ActionChains(driver)
end_item_list = []

# Open browser and connect
try:
    driver.get(target_url)
    logging.info(f"Successfully connected to {target_url}")
except:
    e = sys.exc_info()
    log_warning(f"Error connecting to {target_url}", e)

# Loop to iterate over desired pages
for i in range(5):
    i += 1
    logging.info("Running get_page_items()")

    check_for_cookie_banner()

    # Getting the items from the current page rendering
    item_list = get_page_items()

    for item in item_list:
        try:
            # I originally had the description and url fields saved for two reasons
            # A. If I were scraping this data for myself, I'd like to have these two fields
            # B. I needed a way to ensure I was not getting duplicates during early development
            item_dict = {
                "title": item.find_element_by_class_name("title").text,
                "price": item.find_element_by_class_name("price").text,
                # "description": item.find_element_by_class_name("description").text,
                "reviews": item.find_element_by_class_name("ratings").text,
                # "url": item.find_element_by_class_name("title").get_attribute("href"),
            }
            end_item_list.append(item_dict)
            logging.info(item_dict)
        except:
            e = sys.exc_info()
            log_warning("Encountered an error while creating item_dict", e)
            pass

    # Moving to next pagination
    # This is kind of strange, but it works and it works well.
    x_path = f"/html/body/div[1]/div[3]/div/div[2]/div[2]/button[{i}]"
    logging.info("Looking for pagination button")

    if i == 1:
        logging.info(f"Skipping button {i}")
        pass
    else:
        try:
            button = driver.find_element_by_xpath(x_path)
            logging.info(f"Found pagination button {i}")
            button.click()
            logging.info(f"Pagination button {i} has been clicked")
        except:
            e = sys.exc_info()
            log_warning(f"Failed to find or click pagination button {i}", e)

    # Wait for page to fully load
    logging.info("Waiting for page to reload")
    # Waiting for one second seemed to ensure everything was loaded correctly
    # far more reliably than using WebDriverWait on any element. I was still getting
    # missing pieces due to StaleElementReference errors
    time.sleep(1)

################################# Data Processing ##############################################
def convert_reviews(review):
    stripped_review = re.sub("[^0-9]", "", review)
    return stripped_review


# Processing data pulled from site
# Ask me why I used pandas to create a dataframe and save to csv instead of with open()
try:
    df = pd.DataFrame(end_item_list)
    logging.info("Successfully created dataframe")
except:
    e = sys.exc_info()
    log_warning("Failed to create dataframe", e)

logging.info("Dropping duplicates")
df = df.drop_duplicates()

logging.info("Converting reviews into integers only")
df.reviews = df.reviews.apply(convert_reviews)

df.to_csv("test.csv")

# Close browser upon completion
logging.info(f"Completed site scraping.")
driver.quit()
