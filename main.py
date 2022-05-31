import os

from src import core, utils, menu


with open("token.txt", "r") as fp:
    token = fp.read().strip()
    os.environ["GH_TOKEN"] = token


def parse_section():
    url = input("Enter wildberries catalog url: ")
    driver = core.create_driver("firefox")
    core.section_process(url, driver)


def parse_page():
    url = input("Enter wildberries catalog url: ")
    filename = utils.get_url_name(url)

    print("Create driver...")
    driver_name = core.select_driver_name()
    if driver_name is None:
        print("Quiting...")
        return
    driver = core.create_driver(driver_name)

    core.process_url(url, filename, driver)

    driver.close()


def parse_links_file_sections(filepath: str = "links.txt"):
    driver = core.create_driver("firefox")
    with open(filepath, "r") as fp:
        for url in fp:
            core.section_process(url.strip(), driver)


def main():
    options = ["1. one", "2. section"]
    answers = [parse_page, parse_section]
    menu.select_options(
        options=options,
        answers=answers,
        startMsg="Choose type of parsing",
        answersCallable=True,
    )


if __name__ == "__main__":
    main()
