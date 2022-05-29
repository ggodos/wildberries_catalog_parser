import json
import os
import re
import string
import sys
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import firefox
from selenium.webdriver import chrome
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager

with open("token.txt", "r") as fp:
    token = fp.read().strip()
    os.environ["GH_TOKEN"] = token


def prettify_price(inp_price) -> str:
    stripped_price = inp_price.strip()
    price = ''.join([c if c in string.digits else '' for c in stripped_price])
    return price + stripped_price[-1]


def prettify_old(old_price):
    del_price = str(old_price.contents[1])
    old = re.search("<del>(.+)</del>", del_price)
    if old is None:
        return ""
    old = old.group(1)
    return prettify_price(old)


def parse_product_data(product: str):
    result = dict()
    soup = BeautifulSoup(product, features="lxml")

    low_price = soup.find(attrs={"class": "lower-price"})
    if low_price is not None:
        result["current-price"] = prettify_price(low_price.contents[0])

    old_price = soup.find(attrs={"class": "price-old-block"})
    if old_price is not None:
        result["old-price"] = prettify_old(old_price)

    img = soup.find(name="img")
    if img is not None:
        result["image"] = img.attrs["src"][2:]

    goods_name = soup.find(attrs={"class": "goods-name"})
    if goods_name is not None:
        result["goods-name"] = goods_name.contents[0]

    brand_name = soup.find(attrs={"class": "brand-name"})
    if brand_name is not None:
        result["brand-name"] = brand_name.contents[0]  # pyright:ignore
    return result


def get_page_soup(url: str, driver, delay=10) -> BeautifulSoup:
    driver.get(url)
    try:
        WebDriverWait(driver, delay).until(
            EC.element_to_be_clickable((By.ID, 'filters')))
    except TimeoutException as ex:
        print("Timeout exception")

    soup = BeautifulSoup(driver.page_source, features="lxml")
    return soup


def progress_bar_start(toolbar_width):
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width+1))


def progress_bar_cycle():
    sys.stdout.write("-")
    sys.stdout.flush()


def progress_bar_end():
    sys.stdout.write("]\n")  # this ends the progress bar


def get_soup_products(soup: BeautifulSoup):
    products = soup.find_all(
        attrs={"class":  "product-card j-card-item j-good-for-listing-event"})

    # start progress bar
    toolbar_width = len(products)
    progress_bar_start(toolbar_width)

    data = []
    for product in products:
        to_add = parse_product_data(str(product))
        to_add["id"] = product["id"]
        data.append(to_add)
        progress_bar_cycle()
    progress_bar_end()

    return data


def dump_data(filename: str, data):
    with open(filename, "w", encoding="utf-8") as fp:
        fp.write(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))


def select_driver_name():
    browsers = ["firefox", "chrome"]
    driver_name = ""
    while driver_name not in browsers:
        inp = input("Select browser: \n 1. firefox\n 2. chrome\n ::")
        if not inp.isdigit():
            print("Input must be number.")
            continue
        n = int(inp)
        if n not in [i+1 for i in range(0, len(browsers))]:
            print("Out of range number")
            continue
        driver_name = browsers[n-1]
    return driver_name


def create_driver(driver_name):
    if driver_name == "firefox":
        opts = firefox.options.Options()  # pyright:ignore
        opts.headless = True
        return webdriver.Firefox(service=firefox.service.Service(  # pyright:ignore
            GeckoDriverManager().install()), options=opts)
    elif driver_name == "chrome":
        opts = chrome.options.Options()  # pyright:ignore
        opts.headless = True
        return webdriver.Chrome(service=chrome.service.Service(  # pyright:ignore
            ChromeDriverManager().install()), options=opts)
    raise Exception("No driver used")


def get_pathes(filename):
    dump_directory = os.path.dirname(os.path.realpath(__file__)) + "/target/"
    if not os.path.exists(dump_directory):
        os.mkdir(dump_directory)
    filepath = f"{dump_directory}{filename}"
    fullname = f"{filepath}-full.json"
    idsname = f"{filepath}-ids.json"
    return (fullname, idsname)


def get_url_name(url: str) -> str:
    url_path = urlparse(url).path
    return os.path.basename(url_path)


def process_url(url, filename, driver):
    print(f"Fetching data for {filename}")
    page_soup = get_page_soup(url, driver)
    print(f"Parse data for {filename}...")
    products = get_soup_products(page_soup)
    ids = [item["id"] for item in products]
    fullname, idsname = get_pathes(filename)
    print(f"Writing fulldata in {os.path.basename(fullname)}" +
          f" and only id's in {os.path.basename(idsname)}")
    dump_data(fullname, products)
    dump_data(idsname, ids)


def category_process(url: str, driver):
    n = 1
    filename = get_url_name(url)
    while True:
        writename = f"{filename}_{n}"

        print(f"Fetching data for {writename}...")
        page_soup = get_page_soup(url, driver)

        print(f"Parse data for {writename}...")
        products = get_soup_products(page_soup)
        ids = [item["id"] for item in products]
        fullname, idsname = get_pathes(writename)

        print(f"Writing fulldata in {os.path.basename(fullname)}" +
              f" and only id's in {os.path.basename(idsname)}.")
        dump_data(fullname, products)
        dump_data(idsname, ids)

        next_page = page_soup.find(
            attrs={"class": "pagination-next pagination__next"})
        if next_page is None:
            break
        url = next_page.attrs["href"]  # pyright:ignore
        n+=1


def parse_all_category_pages():
    url = input("Enter wildberries catalog url: ")
    driver = create_driver("firefox")
    category_process(url, driver)


def parse_page():
    url = input("Enter wildberries catalog url: ")
    filename = input("Enter filename: ")

    print("Create driver...")
    driver_name = select_driver_name()
    driver = create_driver(driver_name)

    process_url(url, filename, driver)

    driver.close()


if __name__ == "__main__":
    #  parse_page()
    parse_all_category_pages()
