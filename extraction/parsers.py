import sys
import inspect

from abc import abstractmethod
from bs4 import BeautifulSoup
from collections import defaultdict
from extraction.helpers import *


class BaseParser:
    def __init__(self, html_source):
        self._soup = BeautifulSoup(html_source, 'lxml')

    @property
    @abstractmethod
    def bookmaker(self):
        """The name of the bookmaker being parsed"""

    @property
    @abstractmethod
    def event_type(self):
        """The name of the event type being parsed"""

    @abstractmethod
    def _extract_name_collections(self):
        """
        A list of collection of participant names of events found on that page.

        [(name1, name2), (name3, name6), (name8, name2), ...]
        """

    @abstractmethod
    def _extract_odds_collections(self):
        """
        A list of collection of odds corresponding to the names from the name collection.

        [(odds1, odds2), (odds3, odds4), (odds5, odds6), ...]
        """

    def _create_event(self, name_collection, odds_collection):
        return {
            'bookmaker': self.bookmaker,
            'odds': {name: odds for name, odds in zip(name_collection, odds_collection)}
        }

    def extract_events(self):
        name_cols = self._extract_name_collections()
        odds_cols = self._extract_odds_collections()

        return [self._create_event(name_col, odds_col) for name_col, odds_col in zip(name_cols, odds_cols)
                if collection_valid(name_col, odds_col)]


class Bet365FootballParser(BaseParser):
    bookmaker = 'bet365'
    event_type = 'football'
    draw = True
    _name_div_class = 'rcl-ParticipantFixtureDetails_Team'
    _odds_span_class = 'sgl-ParticipantOddsOnly80_Odds'

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <div>name</div>
        """
        name_extracts = [div.string for div in self._soup.find_all('div', {'class': self._name_div_class})]
        names = insert_draw_placeholders(name_extracts)
        names = clean_names(names, event_type=self.event_type, sub_event=self.sub_event, draw=self.draw)

        return group_elements(names, n=3)

    def _extract_odds_collections(self):
        """
        <span>odds</span>
        """
        odds_extract = [span.string for span in self._soup.find_all('span', {'class': self._odds_span_class})]
        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class BetfredFootballParser(BaseParser):
    bookmaker = 'betfred'
    event_type = 'football'
    draw = True
    _name1_div_class = 'sportsbook-inline-outright__teams-home'
    _name2_div_class = 'sportsbook-inline-outright__teams-away'
    _odds_div_class = 'sportsbook-inline-selection'

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <div>name1</div>
        <div>name2</div>
        """
        name1_extract = [span.string for span in self._soup.find_all('div', {'class': self._name1_div_class})]
        name2_extract = [span.string for span in self._soup.find_all('div', {'class': self._name2_div_class})]
        possible_names = get_possible_names(event_type=self.event_type, sub_event=self.sub_event)

        name_collections = []

        for name1, name2 in zip(name1_extract, name2_extract):
            name_col = (match_name(name1, possible_names), 'draw', match_name(name2, possible_names))
            name_collections.append(name_col)

        return name_collections

    def _extract_odds_collections(self):
        """
        <div><!-- -->odds<!--/ --></div>
        """
        odds_extract = [div.contents[1] for div in self._soup.find_all('div', {'class': self._odds_div_class})]
        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class BetRegalFootballParser(BaseParser):
    bookmaker = 'bet_regal'
    event_type = 'football'
    draw = True
    _name_span_attr = {'data-uat': 'span-ev-list-name-text'}
    _odds_span_attr = {'data-uat': 'ev-list-ev-list-bet-btn-odd'}

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <span>name</span>

        """
        name_extracts = [span.string for span in self._soup.find_all('span', self._name_span_attr)]
        names = insert_draw_placeholders(name_extracts)
        names = clean_names(names, event_type=self.event_type, sub_event=self.sub_event, draw=self.draw)

        return group_elements(names, n=3)

    def _extract_odds_collections(self):
        """
        <span>odds</span>
        """
        odds_extract = [span.string for span in self._soup.find_all('span', self._odds_span_attr)]
        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class BetwayFootballParser(BaseParser):
    bookmaker = 'betway'
    event_type = 'football'
    draw = True
    _name_span_class = 'teamNameEllipsisContainer'
    _odds_div_class = 'odds'

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <span><span>name</span></span>

        header noises --> <span><span>None</span></span>
        """
        name_extracts = [span.span.string for span in self._soup.find_all('span', {'class': self._name_span_class})
                         if span.span.string is not None]
        names = insert_draw_placeholders(name_extracts)
        names = clean_names(names, event_type=self.event_type, sub_event=self.sub_event, draw=self.draw)

        return group_elements(names, n=3)

    def _extract_odds_collections(self):
        """
        <div>odds</div>
        """
        odds_extract = [div.string for div in self._soup.find_all('div', {'class': self._odds_div_class})
                        if div.string is not None]
        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class CoralFootballParser(BaseParser):
    bookmaker = 'coral'
    event_type = 'football'
    draw = True
    _name1_span_attr = {'data-crlat': 'EventFirstName'}
    _name2_span_attr = {'data-crlat': 'EventSecondName'}
    _odds_span_attr = {'data-crlat': 'oddsPrice'}

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <span attr='attr1'>name1</span>
        <span attr='attr2'>name2</span>
        """
        name1_extract = [span.string for span in self._soup.find_all('span', self._name1_span_attr)]
        name2_extract = [span.string for span in self._soup.find_all('span', self._name2_span_attr)]
        possible_names = get_possible_names(event_type=self.event_type, sub_event=self.sub_event)

        name_collections = []

        for name1, name2 in zip(name1_extract, name2_extract):
            name_col = (match_name(name1, possible_names), 'draw', match_name(name2, possible_names))
            name_collections.append(name_col)

        return name_collections

    def _extract_odds_collections(self):
        """
        <span>odds</span>
        """
        odds_extract = [span.string for span in self._soup.find_all('span', self._odds_span_attr)]
        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class LadbrokesFootballParser(BaseParser):
    bookmaker = 'ladbrokes'
    event_type = 'football'
    draw = True
    _name1_a_attr = {'data-crlat': 'EventFirstName'}
    _name2_a_attr = {'data-crlat': 'EventSecondName'}
    _odds_span_attr = {'data-crlat': 'oddsPrice'}

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <a attr='attr1'>name1</a>
        <a attr='attr2'>name2</a>
        """
        name1_extract = [a.string for a in self._soup.find_all('a', self._name1_a_attr)]
        name2_extract = [a.string for a in self._soup.find_all('a', self._name2_a_attr)]
        possible_names = get_possible_names(event_type=self.event_type, sub_event=self.sub_event)

        name_collections = []

        for name1, name2 in zip(name1_extract, name2_extract):
            name_col = (match_name(name1, possible_names), 'draw', match_name(name2, possible_names))
            name_collections.append(name_col)

        return name_collections

    def _extract_odds_collections(self):
        """
        <span>odds</span>
        """
        odds_extract = [span.string for span in self._soup.find_all('span', self._odds_span_attr)]
        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class MrGreenFootballParser(BaseParser):
    bookmaker = 'mr_green'
    event_type = 'football'
    draw = True
    _match_div_attr = {'class': 'KambiBC-bet-offer KambiBC-bet-offer--onecrosstwo KambiBC-bet-offer--inline KambiBC-bet-offer--outcomes-3'}
    _name_div_attr = {'class': 'sc-AxhCb coUVXk'}
    _odds_div_attr = {'class': 'sc-AxheI JhUUD'}

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _get_match_divs(self):
        return self._soup.find_all('div', self._match_div_attr)

    def _extract_name_collections(self):
        """
        must be extracted within match_div otherwise will pick up other odds
        """
        match_divs = self._get_match_divs()
        names = []

        for match_div in match_divs:
            name_extract = [div.string for div in match_div.find_all('div', self._name_div_attr)]
            names.extend(name_extract)

        names = clean_names(names, event_type=self.event_type, sub_event=self.sub_event, draw=self.draw)

        return group_elements(names, n=3)

    def _extract_odds_collections(self):
        match_divs = self._get_match_divs()
        odds_extract = []

        for match_div in match_divs:
            odds = [div.string for div in match_div.find_all('div', self._odds_div_attr)]
            odds_extract.extend(odds)

        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class NovibetFootballParser(BaseParser):
    bookmaker = 'novibet'
    event_type = 'football'
    draw = True
    _name1_span_attr = {'data-bind': "text: Competitor1,TooltipText:{value:Competitor1(),container:'body'}"}
    _name2_span_attr = {'data-bind': "text: Competitor2,TooltipText:{value:Competitor2(),container:'body'}"}
    _odds_div_class = 'odd col-xs-4'

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <span attr='attr1'>name1</span>
        <span attr='attr2'>name2</span>
        """
        name1_extract = [span.string for span in self._soup.find_all('span', self._name1_span_attr)]
        name2_extract = [span.string for span in self._soup.find_all('span', self._name2_span_attr)]
        possible_names = get_possible_names(event_type=self.event_type, sub_event=self.sub_event)

        name_collections = []

        for name1, name2 in zip(name1_extract, name2_extract):
            name_col = (match_name(name1, possible_names), 'draw', match_name(name2, possible_names))
            name_collections.append(name_col)

        return name_collections

    def _extract_odds_collections(self):
        """
        <div><div><!-- ko text: OddsText -->odds<!-- /ko --></div><div>
        """
        odds_extract = [div.div.contents[2] for div in self._soup.find_all('div', {'class': self._odds_div_class})]
        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class PaddyPowerFootballParser(BaseParser):
    bookmaker = 'paddy_power'
    event_type = 'football'
    draw = True
    _name_span_attr = {'ng-class': '$ctrl.className'}
    _odds_span_attr = {'class': 'btn-odds__label'}

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <span>name</span>

        """
        name_extracts = [span.string for span in self._soup.find_all('span', self._name_span_attr)]
        names = insert_draw_placeholders(name_extracts)
        names = clean_names(names, event_type=self.event_type, sub_event=self.sub_event, draw=self.draw)

        return group_elements(names, n=3)

    def _extract_odds_collections(self):
        """
        <span>odds</span>
        """
        odds_extract = [span.string for span in self._soup.find_all('span', self._odds_span_attr)]
        odds = [decimal_odds(odds) for odds in odds_extract]

        return group_elements(odds, n=3)


class UnibetFootballParser(BaseParser):
    bookmaker = 'unibet'
    event_type = 'football'
    draw = True
    _placeholder_name_div_class = '_62278 f59a2'
    _name_div_attr = {'data-test-name': 'teamName'}
    _odds_div_attr = {'data-test-name': 'odds'}

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <div>name</div>
        """
        name_extracts = [div.string for div in self._soup.findAll('div', self._name_div_attr)]
        names = insert_draw_placeholders(name_extracts)
        names = clean_names(names, event_type=self.event_type, sub_event=self.sub_event, draw=self.draw)

        return group_elements(names, n=3)

    def _extract_odds_collections(self):
        """
        <span>Odds</span>
        """
        n_placeholders = self._number_of_placeholder_odds()
        odds_extracts = [span.string for span in self._soup.findAll('span', self._odds_div_attr)][n_placeholders:]
        odds = [decimal_odds(odds) for odds in odds_extracts]

        return group_elements(odds, n=3)

    def _number_of_placeholder_odds(self):
        """
        There are name divs which contribute to odds extract but not names extract. These odds need to be removed
        """
        placeholder_names = [div for div in self._soup.findAll('div', {'class': self._placeholder_name_div_class})]

        return int(len(placeholder_names) * (3/2))


class WilliamHillFootballParser(BaseParser):
    bookmaker = 'william_hill'
    event_type = 'football'
    draw = True
    _name_main_class = 'sp-o-market__title'
    _name_separator = ' v '
    _odds_section_class = 'sp-o-market__buttons'

    def __init__(self, html_source, sub_event):
        super().__init__(html_source)
        self.sub_event = sub_event

    def _extract_name_collections(self):
        """
        <main><a><span>name1 v name2</span></a></main>
        """
        name_extracts = [main.a.span.string for main in self._soup.find_all('main', {'class': self._name_main_class})]
        names = separate_concatenated_names(name_extracts, separator_str=self._name_separator)
        names = insert_draw_placeholders(names)
        names = clean_names(names, event_type=self.event_type, sub_event=self.sub_event, draw=self.draw)

        return group_elements(names, n=3)

    def _extract_odds_collections(self):
        """
        <section><button><span>odds1</span></button><button><span>odds2</span></button><button><span>odds3</span></button></section>
        """
        odds_collections = []

        for section in self._soup.find_all('section', {'class': self._odds_section_class}):
            odds_col = tuple(decimal_odds(button.span.string) for button in section)
            odds_collections.append(odds_col)

        return odds_collections


def get_parsers():
    parser_classes = inspect.getmembers(
        sys.modules[__name__],
        lambda x:
        inspect.isclass(x)
        and issubclass(x, BaseParser)
        and x.__name__ != BaseParser.__name__
    )

    parsers = defaultdict(dict)

    for name, _class in parser_classes:
        parsers[_class.bookmaker][_class.event_type] = _class

    return parsers



