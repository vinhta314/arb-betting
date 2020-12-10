from copy import deepcopy
from extraction.helpers import load_json


class Page:
    def __init__(self, url, bookmaker, event_type, sub_event):
        self.url = url
        self.bookmaker = bookmaker
        self.event_type = event_type
        self.sub_event = sub_event


class Bookmakers:
    BOOKMAKER_CONFIG_PATH = '../config/bookmakers.json'

    def get_pages(self, bookmakers=None, event_types=None, sub_events=None):
        config = self._get_filtered_config(bookmakers, event_types, sub_events)
        pages = []

        for bookmaker, bookmaker_config in config.items():
            for event_type, event_config in bookmaker_config.items():
                for sub_event, url in event_config.items():
                    page = Page(url, bookmaker, event_type, sub_event)
                    pages.append(page)

        return pages

    def _get_filtered_config(self, bookmakers, event_types, sub_events):
        config = load_json(self.BOOKMAKER_CONFIG_PATH)
        if bookmakers:
            self._filter_bookmakers(config, bookmakers)
        if event_types:
            self._filter_event_types(config, event_types)
        if sub_events:
            self._filter_sub_events(config, sub_events)

        return config

    @staticmethod
    def _filter_bookmakers(config, bookmakers: list):
        for bookmaker in deepcopy(config):
            if bookmaker not in bookmakers:
                del config[bookmaker]

    @staticmethod
    def _filter_event_types(config, event_types: list):
        for bookmaker, bookmaker_config in deepcopy(config).items():
            for event_type in bookmaker_config:
                if event_type not in event_types:
                    del config[bookmaker][event_type]

    @staticmethod
    def _filter_sub_events(config, sub_events: list):
        for bookmaker, bookmaker_config in deepcopy(config).items():
            for event_type, event_config in bookmaker_config.items():
                for sub_event in event_config:
                    if sub_event not in sub_events:
                        del config[bookmaker][event_type][sub_event]
