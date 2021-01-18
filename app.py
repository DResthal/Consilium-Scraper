import os
import sys
import time
import re
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import pandas as pd
import logging


formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")


def setup_logger(name, log_file, level=logging.INFO):
    """To setup as many loggers as you want"""

    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)

    return logger


app_log = setup_logger("app_log", "application.log", level=logging.INFO)
error_logger = setup_logger("error_log", "error.log", level=logging.WARNING)


def log_warning(e, msg):
    error_logger.warning(msg)
    error_logger.warning(e)


def check_for_cookie_banner():
    try:
        if driver.find_element_by_id("closeCookieBanner").is_displayed():
            driver.find_element_by_id("closeCookieBanner").click()
            app_log.info("Closed Cookie Banner")
        else:
            app_log.info("Cookie banner not present, nothing to close.")
    except:
        e = sys.exc_info()
        log_warning("Failed to close cookie banner", e)


def get_page_items():
    try:
        item_list = driver.find_elements_by_css_selector("div.thumbnail")
        app_log.info(f"Found item_list")
        return item_list
    except:
        e = sys.exc_info()
        log_warning("Failed to find item_list", e)
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
    app_log.info(f"Successfully connected to {target_url}")
except:
    e = sys.exc_info()
    log_warning(f"Error connecting to {target_url}", e)

# Loop to iterate over desired pages
for i in range(5):
    i += 1
    app_log.info("Running get_page_items()")

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
            app_log.info(item_dict)
        except:
            e = sys.exc_info()
            log_warning("Encountered an error while creating item_dict", e)
            pass

    # Moving to next pagination
    # This is kind of strange, but it works and it works well.
    x_path = f"/html/body/div[1]/div[3]/div/div[2]/div[2]/button[{i}]"
    app_log.info("Looking for pagination button")

    if i == 1:
        app_log.info(f"Skipping button {i}")
        pass
    else:
        try:
            button = driver.find_element_by_xpath(x_path)
            app_log.info(f"Found pagination button {i}")
            button.click()
            app_log.info(f"Pagination button {i} has been clicked")
        except:
            e = sys.exc_info()
            log_warning(f"Failed to find or click pagination button {i}", e)

    # Wait for page to fully load
    app_log.info("Waiting for page to reload")
    # Waiting for one second seemed to ensure everything was loaded correctly
    # far more reliably than using WebDriverWait on any element. I was still getting
    # missing pieces due to StaleElementReference errors
    time.sleep(1)

################################# Data Processing ##############################################
def convert_reviews(review):
    stripped_review = int(re.sub("[^0-9]", "", review))
    return stripped_review


# Processing data pulled from site
# Ask me why I used pandas to create a dataframe and save to csv instead of with open()
try:
    df = pd.DataFrame(end_item_list)
    app_log.info("Successfully created dataframe")
except:
    e = sys.exc_info()
    log_warning("Failed to create dataframe", e)

app_log.info("Dropping duplicates")
df = df.drop_duplicates()

app_log.info("Converting reviews into integers only")
df.reviews = df.reviews.apply(convert_reviews)

df.to_csv("test.csv")

# Close browser upon completion
app_log.info(f"Completed site scraping.")
driver.quit()
