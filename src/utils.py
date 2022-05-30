import json
import os
import re
import string
import sys
from urllib.parse import urlparse
import __main__


def prettify_price(inp_price) -> str:
    stripped_price = inp_price.strip()
    price = ''.join([c if c in string.digits else '' for c in stripped_price])
    return price + stripped_price[-1]


def prettify_old(old_price) -> str:
    del_price = str(old_price.contents[1])
    old = re.search("<del>(.+)</del>", del_price)
    if old is None:
        return ""
    old = old.group(1)
    return prettify_price(old)


def progress_bar_start(toolbar_width: int) -> None:
    sys.stdout.write("[%s]" % (" " * toolbar_width))
    sys.stdout.flush()
    sys.stdout.write("\b" * (toolbar_width+1))


def progress_bar_cycle():
    sys.stdout.write("-")
    sys.stdout.flush()


def progress_bar_end():
    sys.stdout.write("]\n")  # this ends the progress bar


def dump_data(filename: str, data):
    with open(filename, "w", encoding="utf-8") as fp:
        fp.write(json.dumps(data, ensure_ascii=False, sort_keys=True, indent=4))


def get_pathes(filename: str):
    """
    return (fullname, idsname)
    """
    dump_directory = os.path.dirname(os.path.realpath(__main__.__file__)) + "/target/"
    if not os.path.exists(dump_directory):
        os.mkdir(dump_directory)
    filepath = f"{dump_directory}{filename}"
    fullname = f"{filepath}-full.json"
    idsname = f"{filepath}-ids.json"
    return (fullname, idsname)


def get_url_name(url: str) -> str:
    url_path = urlparse(url).path
    return os.path.basename(url_path)
