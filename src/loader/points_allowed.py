"""
Implements the data loading for points allowed.

Fantasy Points Allowed is a metric that indicates how good or bad
each NFL defense is at limiting fantasy production to their
opponents. Teams that rank in the top 8 surrender the most fantasy
points. They represent easy matchups that fantasy owners should
target. On the flip side, teams that rank in the bottom 8 are
difficult matchups that fantasy owners should take into
consideration for start/sit decisions.

Most recent years (back to 2015) are available. However, in some
cases, e.g. Las Vegas Raiders, the name of the team has changed.
Since team names are kept up to date, the points allowed for such a
team are not available. Further, the points of the previous name are
not available too.
"""
import bs4
import pandas as pd
import requests

from abc import ABC

from config.mapping import pa_type, team_map
from src.loader.loader import Loader


class PointsAllowed(Loader, ABC):
    def __init__(self, year):
        Loader.__init__(self)

        self.year = year

        self.filename = f"points_allowed_{self.year}.csv"
        self.dir = f"../raw/points_allowed"
        self.url = f"https://www.fantasypros.com/nfl/points-allowed.php?year={self.year}"

    def clean_data(self, df):
        """ Cleans data specifically for points allowed. """
        # drop unnamed columns
        df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

        # assign better column names
        df.columns = list(pa_type.keys())

        # assign team shortcut
        df["team"] = df["team"].apply(add_team_shortcut)

        # add year
        df["year"] = self.year

        # set column types
        return df.astype(pa_type)

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

        # in that specific case, the content of the table is within one single list
        data_mod = list()
        data_mod.append(data[0])
        for i in range(0, len(data[1]), 13):
            data_mod.append(data[1][i:i+13])

        # return as pandas DataFrame
        return pd.DataFrame(data_mod[1:], columns=data[0])


def add_team_shortcut(team):
    """ Replaces team name with commonly used shortcut. """
    return team_map[team]
