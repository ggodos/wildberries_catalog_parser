import os

import bs4
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver import chrome, firefox
from selenium.webdriver.chrome import options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.firefox import GeckoDriverManager
from webdriver_manager.core.utils import ChromeType

from src import utils, menu


def parse_product_data(product: str):
    """parse_product_data.

    :param product:
    :type product: str
    """
    result = {}

    soup = BeautifulSoup(product, features="lxml")

    low_price = soup.find(attrs={"class": "lower-price"})
    if isinstance(low_price, bs4.element.Tag):
        result["current-price"] = utils.prettify_price(low_price.contents[0])

    old_price = soup.find(attrs={"class": "price-old-block"})
    if isinstance(old_price, bs4.element.Tag):
        result["old-price"] = utils.prettify_old(old_price)

    img = soup.find(name="img")
    if isinstance(img, bs4.element.Tag):
        img_url = f"https:{img.attrs['src']}"
        result["image"] = img_url

    goods_name = soup.find(attrs={"class": "goods-name"})
    if isinstance(goods_name, bs4.element.Tag):
        result["goods-name"] = str(goods_name.contents[0]).strip()

    brand_name = soup.find(attrs={"class": "brand-name"})
    if isinstance(brand_name, bs4.element.Tag):
        result["brand-name"] = str(brand_name.contents[0]).strip()
    return result


def get_page_soup(url: str, driver, delay=10) -> BeautifulSoup:
    """get_page_soup.

    :param url:
    :type url: str
    :param driver:
    :param delay:
    :rtype: BeautifulSoup
    """
    driver.get(url)
    try:
        WebDriverWait(driver, delay).until(
            EC.element_to_be_clickable((By.ID, "filters"))
        )
    except TimeoutException:
        print("Timeout exception")

    page_soup = BeautifulSoup(driver.page_source, features="lxml")
    return page_soup


def get_soup_products(soup: BeautifulSoup):
    """get_soup_products.

    :param soup:
    :type soup: BeautifulSoup
    """
    products = soup.find_all(
        attrs={"class": "product-card j-card-item j-good-for-listing-event"}
    )

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


def select_driver_name():
    """select_driver_name.

    :rtype: str | None
    """
    while True:
        options = ["1. brave", "2. firefox", "3. chrome"]
        answers = ["brave", "firefox", "chrome"]
        answer = menu.select_options(
            options=options, answers=answers, startMsg="Select browser"
        )
        if answer is None:
            print("error")
        return answer


def create_driver(driver_name: str):
    """create_driver.

    :param driver_name:
    :type driver_name: str
    """
    if driver_name == "brave":
        opts = webdriver.ChromeOptions()
        opts.headless = True
        return webdriver.Chrome(
            service=chrome.service.Service(
                ChromeDriverManager(chrome_type=ChromeType.BRAVE).install()
            ),
            options=opts,
        )
    if driver_name == "firefox":
        opts = firefox.options.Options()
        opts.headless = True
        return webdriver.Firefox(
            service=firefox.service.Service(GeckoDriverManager().install()),
            options=opts,
        )
    if driver_name == "chrome":
        opts = webdriver.ChromeOptions()
        opts.headless = True
        return webdriver.Chrome(
            service=chrome.service.Service(ChromeDriverManager().install()),
            options=opts,
        )
    raise Exception("Wrong driver_name")


def process_url(url: str, filename: str, driver, silent=False):
    """process_url.

    :param url:
    :type url: str
    :param filename:
    :type filename: str
    :param driver:
    :param silent:
    """
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
    """section_process.

    :param url:
    :type url: str
    :param driver:
    :param silent:
    """
    filename_number = 1
    filename = utils.get_url_name(url)
    while True:
        writename = f"{filename}_{filename_number}"
        if not silent:
            print(f"Fetching data for {writename}...")
        page_soup = get_page_soup(url, driver)

        if not silent:
            print(f"Parse data for {writename}...")
        products = get_soup_products(page_soup)
        ids = [item["id"] for item in products]
        fullname, idsname = utils.get_pathes(writename)

        if not silent:
            print(
                f"Writing fulldata in {os.path.basename(fullname)}"
                + f" and only id's in {os.path.basename(idsname)}."
            )
        utils.dump_data(fullname, products)
        utils.dump_data(idsname, ids)

        next_page = page_soup.find(
            attrs={"class": "pagination-next pagination__next"}
        )
        if next_page is None:
            break
        url = next_page.attrs["href"]  # pyright:ignore
        filename_number += 1
