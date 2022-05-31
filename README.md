# This is wildberries.ru catalog parser

## Dependecies

---

- selenium
- beautifulsoup4
- lxml
- webdriver-manager

## Installation

---

    pip install -r requirements.txt

## Usage

---

1. Generate github token and add it to token.txt (need for webdriver manager)
1. Run main.py
1. Choose parse type
   - one - parse only given url
   - section - parse url and select next page while can
1. Enter start url
1. Choose browser
1. Enjoy

## Info

---

- All data saved in `target` directory
- List of supported browsers:
  - Brave
  - Chrome
  - Firefox
