import os
from src.core import create_driver, section_process, select_driver_name, process_url
from simple_term_menu import TerminalMenu
import src.utils as utils


with open("token.txt", "r") as fp:
    token = fp.read().strip()
    os.environ["GH_TOKEN"] = token


def parse_section():
    url = input("Enter wildberries catalog url: ")
    driver = create_driver("firefox")
    section_process(url, driver)


def parse_page():
    url = input("Enter wildberries catalog url: ")
    filename = utils.get_url_name(url)

    print("Create driver...")
    driver_name = select_driver_name()
    driver = create_driver(driver_name)

    process_url(url, filename, driver)

    driver.close()


def parse_links_file_sections(filepath: str = "links.txt"):
    driver = create_driver("firefox")
    with open(filepath, "r") as fp:
        for url in fp:
            section_process(url.strip(), driver)


if __name__ == "__main__":
    options = ["[o] one", "[s] section"]
    simple_term_menu = TerminalMenu(options, title="What to parse")
    menu_entry_index = simple_term_menu.show()
    if menu_entry_index == 0:
        parse_page()
    elif menu_entry_index == 1:
        parse_section()
