import time

from selenium import webdriver
from extraction.helpers import load_json

#TODO: fix opening containers, why isnt the web page opening full screen!? use to but not after scrolling?


class Browser:
    _WEBDRIVER_PATH = '../../webdrivers/chromedriver'

    _scrollers = ['bet_regal']
    _containers = ['mr_green']
    _container_div_class = 'KambiBC-collapsible-container KambiBC-mod-event-group-container'

    def __init__(self):
        self.browser = self._setup_browser()

    def get_page_sources(self, url, bookmaker=None):
        self.browser.get(url)
        time.sleep(10)

        if bookmaker in self._containers:
            self._open_page_containers()

        if bookmaker in self._scrollers:
            page_sources = self._get_page_sources_from_scrolling()
        else:
            page_sources = [self.browser.page_source]

        return page_sources

    def _get_page_sources_from_scrolling(self):
        page_sources = []
        window_height = self._get_window_height()
        page_height = self._get_page_height()
        y = 0

        while y < page_height:
            self.browser.execute_script(f'window.scrollTo(0, {y});')
            page_sources.append(self.browser.page_source)
            time.sleep(2)
            y += window_height

        self.browser.execute_script(f'window.scrollTo(0, 0);')

        return page_sources

    def _open_page_containers(self):
        containers = self.browser.find_elements_by_xpath(f"//div[@class='{self._container_div_class}']")
        window_height = self._get_window_height()
        y = 0

        while len(containers) > 0:
            try:
                containers[0].click()
                tried = False
            except:
                tried = True

            time.sleep(10)
            containers = self.browser.find_elements_by_xpath(f"//div[@class='{self._container_div_class}']")

            if tried:
                y += int(window_height/2)
                self.browser.execute_script(f'window.scrollTo(0, {y});')

        self.browser.execute_script(f'window.scrollTo(0, 0);')



    def _get_page_height(self):
        return self.browser.execute_script("return document.body.scrollHeight")

    def terminate(self):
        self.browser.quit()

    def _get_window_height(self):
        return self.browser.get_window_size()['height']

    def _setup_browser(self):
        options = self._setup_options()
        browser = webdriver.Chrome(options=options, executable_path=self._WEBDRIVER_PATH)
        self._execute_chrome_commands(browser)

        return browser

    def _setup_options(self):
        options = webdriver.ChromeOptions()
        options.add_experimental_option('excludeSwitches', ['enable-automation'])
        options.add_experimental_option('useAutomationExtension', False)

        return options

    @staticmethod
    def _execute_chrome_commands(browser):
        """
        Masking the webdriver to prevent sites from blocking content to selenium
        """
        cmd1 = 'Page.addScriptToEvaluateOnNewDocument'
        cmd1_args = {
            'source': """
            Object.defineProperty(navigator, 'webdriver', {

            get: () => undefined

            })
            """
        }

        cmd2 = 'Network.setUserAgentOverride'
        cmd2_args = {
            'userAgent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'
        }

        browser.execute_cdp_cmd(cmd1, cmd1_args)
        browser.execute_cdp_cmd(cmd2, cmd2_args)
