import os

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
from simple_term_menu import TerminalMenu

import src.utils as utils


def parse_product_data(product: str):
    result = dict()
    soup = BeautifulSoup(product, features="lxml")

    low_price = soup.find(attrs={"class": "lower-price"})
    if low_price is not None:
        result["current-price"] \
            = utils.prettify_price(low_price.contents[0])  # type: ignore

    old_price = soup.find(attrs={"class": "price-old-block"})
    if old_price is not None:
        result["old-price"] = utils.prettify_old(old_price)

    img = soup.find(name="img")
    if img is not None:
        result["image"] = img.attrs["src"][2:]  # type: ignore

    goods_name = soup.find(attrs={"class": "goods-name"})
    if goods_name is not None:
        result["goods-name"] = \
            (goods_name.contents[0]).strip()  # type: ignore

    brand_name = soup.find(attrs={"class": "brand-name"})
    if brand_name is not None:
        result["brand-name"] \
            = (brand_name.contents[0]).strip()  # type: ignore
    return result


def get_page_soup(url: str, driver, delay=10) -> BeautifulSoup:
    driver.get(url)
    try:
        WebDriverWait(driver, delay).until(
            EC.element_to_be_clickable((By.ID, 'filters')))
    except TimeoutException:
        print("Timeout exception")

    page_soup = BeautifulSoup(driver.page_source, features="lxml")
    return page_soup


def get_soup_products(soup: BeautifulSoup):
    products = soup.find_all(
        attrs={"class":  "product-card j-card-item j-good-for-listing-event"})

    # start progress bar
    toolbar_width = len(products)
    utils.progress_bar_start(toolbar_width)

    data = []
    for product in products:
        to_add = parse_product_data(str(product))
        to_add["id"] = product["id"]
        data.append(to_add)
        utils.progress_bar_cycle()
    utils.progress_bar_end()

    return data


def select_driver_name() -> str:
    options = ["[f] firefox", "[c] chrome"]
    terminal_menu = TerminalMenu(options)
    menu_entry_index = terminal_menu.show()
    if menu_entry_index == 0:
        return "firefox"
    elif menu_entry_index == 1:
        return "chome"
    return ""


def create_driver(driver_name: str):
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
    raise Exception("Wrong driver_name")


def process_url(url: str, filename: str, driver, silent=False):
    if not silent:
        print(f"Fetching data for {filename}")
    page_soup = get_page_soup(url, driver)

    if not silent:
        print(f"Parse data for {filename}...")
    products = get_soup_products(page_soup)
    ids = [item["id"] for item in products]
    fullname, idsname = utils.get_pathes(filename)

    if not silent:
        print("Write data in: ")
        print(fullname)
        print(idsname)
    utils.dump_data(fullname, products)
    utils.dump_data(idsname, ids)


def section_process(url: str, driver, silent=False):
    n = 1
    filename = utils.get_url_name(url)
    while True:
        writename = f"{filename}_{n}"
        if not silent:
            print(f"Fetching data for {writename}...")
        page_soup = get_page_soup(url, driver)

        if not silent:
            print(f"Parse data for {writename}...")
        products = get_soup_products(page_soup)
        ids = [item["id"] for item in products]
        fullname, idsname = utils.get_pathes(writename)

        if not silent:
            print(f"Writing fulldata in {os.path.basename(fullname)}" +
                  f" and only id's in {os.path.basename(idsname)}.")
        utils.dump_data(fullname, products)
        utils.dump_data(idsname, ids)

        next_page = page_soup.find(
            attrs={"class": "pagination-next pagination__next"})
        if next_page is None:
            break
        url = next_page.attrs["href"]  # pyright:ignore
        n += 1
