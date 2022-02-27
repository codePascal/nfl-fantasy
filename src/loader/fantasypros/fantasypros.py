"""
Implements the data handling for data fetched from
https://www.fantasypros.com/nfl. If the data is not available
offline, it is freshly fetched from the website.

The recorded fantasy points correspond to standard scoring. For other
scoring schemes, e.g. PPR or Half-PPR, the stats can be used to
calculate points scored in that specific scheme.
"""
import bs4
import pandas as pd
import requests

from abc import ABC

from src.loader.loader import Loader


class FantasyProsLoader(Loader, ABC):
    def __init__(self, year, refresh=False):
        Loader.__init__(self, refresh)
        self.year = year

    def get_html_content(self):
        """ Reads HTML content and returns data table. """
        # get HTML config
        print("Fetching from", self.url)
        req = requests.get(self.url)

        # observe HTML output -> https://webformatter.com/html
        # print(req.text)

        # get table raw
        soup = bs4.BeautifulSoup(req.content, "html.parser")
        table = soup.find(id="data")
        data = self.get_table_data(table)

        # return as pandas DataFrame
        return pd.DataFrame(data[1:], columns=data[0])
