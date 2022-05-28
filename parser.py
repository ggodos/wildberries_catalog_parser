from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup
import re
import os
import json
import sys
import string


os.environ["GH_TOKEN"] = "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"


def pretty_price(inp_price) -> str:
    stripped = inp_price.strip()
    price = ''.join([c if c in string.digits else '' for c in stripped])
    return price + stripped[-1]


def pretty_old(old_price) -> str:
    del_price = str(old_price.contents[1])
    old = re.search("<del>(.+)</del>", del_price)
    if old is None:
        return ""
    old = old.group(1)
    return pretty_price(old)


def parse_product_data(product: str):
    result = dict()
    soup = BeautifulSoup(product, features="lxml")
    low_price = soup.find(attrs={"class": "lower-price"})
    if low_price is not None:
        result["lower-price"] = \
            pretty_price(low_price.contents[0])  # pyright:ignore
    old_price = soup.find(attrs={"class": "price-old-block"})
    if old_price is not None:
        result["old_price"] = pretty_old(old_price)
    img = soup.find(name="img")
    if img is not None:
        result["img"] = img.attrs["src"][2:]  # pyright:ignore
    goods_name = soup.find(attrs={"class": "goods-name"})
    if goods_name is not None:
        result["goods-name"] = goods_name.contents[0]  # pyright:ignore
    brand_name = soup.find(attrs={"class": "brand-name"})
    if brand_name is not None:
        result["brand-name"] = brand_name.contents[0]  # pyright:ignore
    return result


def getSoup(url, delay=15):
    print("Create driver...")
    # Options
    opts = Options()
    opts.headless = True
    driver = webdriver.Firefox(service=Service(  # pyright:ignore
        GeckoDriverManager().install()), options=opts)

    # Fetch
    print("Start fetching data...")
    driver.get(url)
    try:
        WebDriverWait(driver, delay).until(
            EC.element_to_be_clickable((By.ID, 'filters')))
    except:
        print("Error of loading")

    soup = BeautifulSoup(driver.page_source, features="lxml")

    driver.close()
    return soup


def parseSoup(soup: BeautifulSoup, element_class="product-card j-card-item j-good-for-listing-event"):
    print("Start parsing...")
    products = soup.find_all(attrs={"class": element_class})
    data = []
    toolbar_width = len(products)

    # start progress bar
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width+1))
    for product in products:
        to_add = parse_product_data(str(product))
        to_add["id"] = product["id"]
        data.append(to_add)

        sys.stdout.write("-")
        sys.stdout.flush()

    sys.stdout.write("]\n")  # this ends the progress bar

    return data


def dumpData(filename: str, data):
    with open(filename, "w") as fp:
        fp.write(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))


def main():
    url = input("Enter wildberries catalog url: ")
    filename = input("Enter filename: ")
    directory = os.getcwd() + "/target/"
    if not os.path.exists(directory):
        os.mkdir(directory)
    filename = f"{directory}{filename}"
    fullname = f"{filename}-full.json"
    idsname = f"{filename}-ids.json"

    soup = getSoup(url)
    results = parseSoup(
        soup, "product-card j-card-item j-good-for-listing-event")
    print(f"Writing fulldata in {os.path.basename(fullname)}" +
          f"and only id's in {os.path.basename(idsname)}")
    dumpData(fullname, results)
    ids = [item["id"] for item in results]
    dumpData(idsname, ids)


if __name__ == "__main__":
    main()
