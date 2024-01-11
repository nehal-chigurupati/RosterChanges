import numpy as np
import pandas as pd
from sqlalchemy import create_engine

def next_season(current_season):
    """
    Function to return the next season given a season in the format "YYYY-YY".
    """
    start_year, end_year_suffix = current_season.split('-')

    start_year = int(start_year)
    end_year_suffix = int(end_year_suffix)

    next_start_year = start_year + 1
    next_end_year_suffix = end_year_suffix + 1

    #Handle the case when moving into a new decade
    if next_end_year_suffix < 10:
        next_end_year_suffix = f'0{next_end_year_suffix}'

    return f'{next_start_year}-{next_end_year_suffix}'

def get_last_year_from_season(season):
    """
    Takes in a season in format "2000-01" and returns the last year in that season ("2001")
    """
    start_year, end_year_fragment = season.split('-')

    end_year = start_year[:2] + end_year_fragment

    return end_year


def pct_change_rosters(initial_roster, final_roster):
    A = []
    B = []
    for index, row in initial_roster.iterrows():
        A.append(row["PLAYER_ID"])
    for index, row in final_roster.iterrows():
        B.append(row["PLAYER_ID"])

    common_count = len([item for item in A if item in B])

    # Calculate the proportion
    proportion = common_count / len(A) if A else 0  # Check if A is not empty to avoid division by zero

    return 1 - proportion
