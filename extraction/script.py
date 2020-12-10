import logging

from extraction.parsers import get_parsers
from extraction.browser import Browser
from extraction.bookmakers import Bookmakers
from database.events_db import EventsDB
from exceptions import ExtractionError


logging.basicConfig(
    format='%(asctime)s: %(message)s',
    level=logging.INFO,
    datefmt='%Y-%m-%d %H:%M'
)


if __name__ == '__main__':
    browser = Browser()
    parsers = get_parsers()
    events_db = EventsDB()
    pages = Bookmakers().get_pages(
        bookmakers=['mr_green'],
        sub_events=['england:premier-league', 'england:championship']
    )

    for page in pages:

        html_sources = browser.get_page_sources(page.url, bookmaker=page.bookmaker)

        logging.info(f'Parsing page: {page.bookmaker} | {page.event_type} | {page.sub_event}')
        try:
            for html_source in html_sources:
                parser = parsers[page.bookmaker][page.event_type](html_source, page.sub_event)
                events = parser.extract_events()
                print(events)
        except ExtractionError as error:
            logging.info(error)

    browser.terminate()







