import os
import sys
import time
import json
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
import pandas as pd
import logging

logging.basicConfig(
    level=logging.INFO,
    filename="alog.log",
    format="%(asctime)s: %(levelname)s: %(message)s",
)

# Get all items, prices and number of reviews on first 5 pages.
target_url = "https://webscraper.io/test-sites/e-commerce/ajax/computers/laptops"
webdriver_path = os.path.abspath("chromedriver_win32\chromedriver.exe")

driver = webdriver.Chrome(webdriver_path)

try:
    driver.get(target_url)
    logging.info(f"Successfully connected to {target_url}")
except:
    e = sys.exc_info()
    logging.warning(f"Error connecting to {target_url}")
    logging.warning(e)

try:
    if driver.find_element_by_id("closeCookieBanner").is_displayed():
        driver.find_element_by_id("closeCookieBanner").click()
        logging.info("Closed Cookie Banner")
except:
    e = sys.exc_info()
    logging.warning("Faile to close cookie banner")
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


action = ActionChains(driver)

end_item_list = []

for i in range(5):
    i += 1
    logging.info("Running get_page_items()")
    print(i)
    item_list = get_page_items()
    for item in item_list:
        try:
            item_dict = {
                "title": item.find_element_by_class_name("title").text,
                "price": item.find_element_by_class_name("price").text,
                "description": item.find_element_by_class_name("description").text,
                "reviews": item.find_element_by_class_name("ratings").text,
                "url": item.find_element_by_class_name("title").get_attribute("href"),
            }
            end_item_list.append(item_dict)
            logging.info(item_dict)
        except:
            e = sys.exc_info()
            print(e)
            pass

    x_path = f"/html/body/div[1]/div[3]/div/div[2]/div[2]/button[{i}]"
    print(f"xpath: {x_path}")
    logging.info("Looking for pagination button")

    if i != 1:
        try:
            button = driver.find_element_by_xpath(x_path)
            logging.info("Found pagination button")
            button.click()
            logging.info("Pagination button has been clicked")
        except:
            e = sys.exc_info()
            logging.warning("Failed to find or click pagination button")
            logging.warning(e)
    else:
        print(f"Skipping {i}")
        pass

    time.sleep(1)

df = pd.DataFrame(end_item_list)
df = df.drop_duplicates()
df.to_csv("test.csv")

driver.quit()
