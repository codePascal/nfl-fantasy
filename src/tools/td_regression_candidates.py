"""
Evaluates the TD regression candidates for a given position regarding
the mean. A high or low touchdown total is not predictive for future
performance as these players will often regress towards the mean or
average the following year.
"""
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import tqdm

import src.preprocessing.playbyplay.playbyplay as pbp
from src.preprocessing.statistics.statistics import Statistics

sns.set_style("whitegrid")


def fix_player_names(name):
    split = name.split()
    first_initial = split[0][0]
    last_name = split[1]
    return '.'.join([first_initial, last_name])


if __name__ == "__main__":
    # year
    year = 2021

    # position and play combinations
    comb = [("QB", "pass"), ("QB", "rush"), ("RB", "rush"), ("RB", "rec"), ("WR", "rec"), ("TE", "rec")]
    for position, play in comb:
        # load historical play-by-play data
        if not os.path.exists(f"../preprocessed/play-by-play/pbp_1999to{year}.csv"):
            df_prob = pbp.concat_playbyplay_data((1999, year))
            df_prob = df_prob.loc[:, ["rush_attempt", "rush_touchdown", "pass_attempt", "pass_touchdown",
                                      "yardline_100", "two_point_attempt", "year"]]
        else:
            df_prob = pd.DataFrame()
            chunks = pd.read_csv(f"../preprocessed/play-by-play/pbp_1999to{year}.csv", iterator=True, low_memory=False,
                                 chunksize=10000)
            for chunk in tqdm.tqdm(chunks):
                chunk = chunk.loc[:, ["rush_attempt", "rush_touchdown", "pass_attempt", "pass_touchdown",
                                      "yardline_100", "two_point_attempt", "year"]]
                df_prob = pd.concat([df_prob, chunk])

        # select data from previous years
        df_prob = df_prob.loc[(df_prob["year"] < year)]

        # select pass or run attempts
        if play == "pass" or play == "rec":
            # passing/receiving: pass attempt that ended in a touchdown
            df_prob = df_prob.loc[:, ["pass_attempt", "pass_touchdown", "yardline_100", "two_point_attempt"]]
            df_prob = df_prob.rename({"pass_attempt": "attempt", "pass_touchdown": "touchdown"}, axis=1)
        elif play == "rush":
            # rushing: rush attempt that ended in a touchdown
            df_prob = df_prob.loc[:, ["rush_attempt", "rush_touchdown", "yardline_100", "two_point_attempt"]]
            df_prob = df_prob.rename({"rush_attempt": "attempt", "rush_touchdown": "touchdown"}, axis=1)

        # select only normal attempts
        df_prob = df_prob.loc[(df_prob["two_point_attempt"] == 0) & (df_prob["attempt"] == 1)]

        # find probability of scoring a touchdown depending on distance to endzone
        df_prob = df_prob.groupby("yardline_100")["touchdown"].value_counts(normalize=True)
        df_prob = pd.DataFrame({"probability_of_touchdown": df_prob.values}, index=df_prob.index).reset_index()

        # keep stats where touchdown was scored and drop column
        df_prob = df_prob.loc[(df_prob["touchdown"] == 1)]
        df_prob = df_prob.drop("touchdown", axis=1)

        # plot probability of scoring a touchdown
        df_prob.plot(x="yardline_100", y="probability_of_touchdown", title=f"Probability for {play}ing TD")
        plt.savefig(f"../reports/td_regression_candidates/touchdown_probability_{play}.png")

        # load play-by-play data for defined year
        if not os.path.exists(f"../raw/play-by-play/play_by_play_{year}.csv"):
            df_train = pbp.get_playbyplay_data(year)
        else:
            df_train = pd.DataFrame()
            chunks = pd.read_csv(f"../raw/play-by-play/play_by_play_{year}.csv", iterator=True, low_memory=False,
                                 chunksize=10000, index_col=0)
            for chunk in tqdm.tqdm(chunks):
                df_train = pd.concat([df_train, chunk])

        # get player, team and distance to endzone
        if play == "pass":
            df_train = df_train.loc[:, ["passer_player_name", "posteam", "yardline_100"]]
        elif play == "rec":
            df_train = df_train.loc[:, ["receiver_player_name", "posteam", "yardline_100"]]
        elif play == "rush":
            df_train = df_train.loc[:, ["rusher_player_name", "posteam", "yardline_100"]]
        df_train = df_train.dropna()

        # rename features
        df_train = df_train.rename(columns={df_train.columns[0]: "player", "posteam": "team"})

        # join probability with training
        data = df_train.merge(df_prob, how="left", on="yardline_100")

        # group by player and team and sum up expected touchdowns
        data = data.groupby(["player", "team"], as_index=False).agg({"probability_of_touchdown": np.sum}).rename(
            {"probability_of_touchdown": "Expected touchdowns"}, axis=1)
        data = data.sort_values(by="Expected touchdowns", ascending=False)

        # rank the expected touchdowns
        data["Expected touchdowns rank"] = data["Expected touchdowns"].rank(ascending=False)

        # load final stats
        df_actual = Statistics(position, year).get_accumulated_data()

        # get player, team and td
        if play == "pass":
            df_actual = df_actual.loc[:, ["player", "team", "passing_td"]]
            df_actual = df_actual.rename({"passing_td": "touchdowns"}, axis=1)
        elif play == "rec":
            df_actual = df_actual.loc[:, ["player", "team", "receiving_td"]]
            df_actual = df_actual.rename({"receiving_td": "touchdowns"}, axis=1)
        elif play == "rush":
            df_actual = df_actual.loc[:, ["player", "team", "rushing_td"]]
            df_actual = df_actual.rename({"rushing_td": "touchdowns"}, axis=1)

        # clean up player names
        df_actual["player"] = df_actual["player"].apply(fix_player_names)

        # summarize the year
        df_actual = df_actual.groupby(["player", "team"]).agg({"touchdowns": np.sum}).reset_index()

        # merge raw and drop position
        data = df_actual.merge(data, how="left", on=["player", "team"]).dropna()

        # rename features and calculate rank of actual touchdowns
        data = data.rename({"touchdowns": "Actual touchdowns"}, axis=1)
        data["Actual touchdowns rank"] = data["Actual touchdowns"].rank(ascending=False)

        # calculate regression candidate
        data["Regression candidate"] = data["Expected touchdowns"] - data["Actual touchdowns"]
        data["Regression rank candidate"] = data["Actual touchdowns rank"] - data["Expected touchdowns rank"]

        # make simple true/false column for regression candidate
        data["Positive regression candidate"] = data["Regression candidate"] > 0

        # explore the statistics
        fig, ax = plt.subplots(figsize=(12, 8))
        ax.set_title(f"Positive regression candidates for {play} {position} in season {year}")

        # plot expected vs actual touchdowns and incorporate regression candidate values
        sns.scatterplot(
            x="Expected touchdowns",
            y="Actual touchdowns",
            hue="Positive regression candidate",
            data=data,
            palette=['r', 'g']
        )

        # plot line denoting border to positive/negative regression candidate
        max_actual_td = int(data["Actual touchdowns"].max())
        max_expected_td = int(data["Expected touchdowns"].max())
        max_td = max(max_actual_td, max_expected_td)
        sns.lineplot(x=range(max_td), y=range(max_td))

        # show top five negative and positive regression candidates
        data_sorted = data.sort_values(by="Regression candidate", ascending=False).reset_index()
        for i, row in data_sorted.iterrows():
            if i <= 1 or i >= len(data_sorted) - 1 - 1:
                ax.text(
                    x=row["Expected touchdowns"] + 0.1,
                    y=row["Actual touchdowns"] + 0.05,
                    s=row["player"]
                )

        # save
        data_sorted.to_csv(
            f"../reports/td_regression_candidates/td_regression_candidates_{play}_{position}_{year}.csv",
            index=False
        )
        plt.savefig(
            f"../reports/td_regression_candidates/regression_candidates_{play}_{position}_{year}.png"
        )
