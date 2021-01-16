import os
import sys
import time
import json
from selenium import webdriver
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


list_of_items = driver.find_element_by_class_name("ecomerce-items").get_attribute(
    "data-items"
)


json_of_items = json.loads(list_of_items)

logging.info(json.dumps(json_of_items, sort_keys=True, indent=2))

driver.quit()
