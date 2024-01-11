import numpy as np
import pandas as pd
from nba_api.stats.static import teams
from nba_api.stats.endpoints import teamestimatedmetrics, commonteamroster, teamyearbyyearstats, teamgamelog
from sqlalchemy import create_engine

def get_all_teams():
    team_abbrevs = []
    team_ids = []
    for team in teams.get_teams():
        team_abbrevs.append(team["abbreviation"])
        team_ids.append(team['id'])
    

    return pd.DataFrame({'ABBREV': team_abbrevs, "ID": team_ids})

def get_team_seasons_data(team_id):
    data = teamyearbyyearstats.TeamYearByYearStats(league_id="00", per_mode_simple="Totals", season_type_all_star="Regular Season", team_id=team_id)
    return data.get_data_frames()[0]

def get_season_advanced_stats(season):
    data = teamestimatedmetrics.TeamEstimatedMetrics(league_id="00", season=season, season_type="Regular Season")
    return data.get_data_frames()[0]

def get_roster(team_id, season):
    data = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
    return data.get_data_frames()[0]

def get_playoff_win_count(team_id, season):
    # Get all teams
    nba_teams = teams.get_teams()

    # Get playoff game log for the team in the specified season
    gamelog = teamgamelog.TeamGameLog(team_id=team_id, season=season, season_type_all_star='Playoffs')

    # Extract the DataFrame
    games = gamelog.get_data_frames()[0]

    # Count wins
    wins = len(games[games['WL'] == 'W'])

    return wins


#Connect to sqlite database
engine = create_engine("sqlite:///Data/team_database.db")

#Get all team abbreviations and their corresponding IDs
team_info = get_all_teams()
team_info.to_sql("TEAM_IDS", engine, if_exists="replace", index=False)

#Get all seasons each team has played
seasons = []
for index, row in team_info.iterrows():
    seasons.append(get_team_seasons_data(row['ID']))

team_seasons = pd.concat(seasons)
team_seasons.to_sql("TEAM_SEASONS", engine, if_exists="replace", index=False)


#Get advanced data from each season

season_data = []
for season in np.unique(team_seasons["YEAR"]):
    advanced_data = get_season_advanced_stats(season)
    advanced_data.insert(0, "SEASON", [season]*len(advanced_data), True)
    season_data.append(advanced_data)

all_seasons_advanced_data = pd.concat(season_data)
all_seasons_advanced_data.to_sql("TEAM_SEASON_ADVANCED_DATA", engine, if_exists="replace", index=False)

#Get rosters for each team season

season_rosters = []
counter = 1
for index, row in team_seasons.iterrows():
    season_rosters.append(get_roster(row["TEAM_ID"], row["YEAR"]))
    print("Collecting team roster " + str(counter) +"/" + str(len(team_seasons)))
    counter += 1

season_rosters = pd.concat(season_rosters)
season_rosters.to_sql("TEAM_SEASON_ROSTERS", engine, if_exists="replace", index=False)

#Get playoff win count for each team season
num_playoff_wins = []
counter = 1
for index, row in team_seasons.iterrows():
    num_playoff_wins.append(get_playoff_win_count(row["TEAM_ID"], row["YEAR"]))
    print("Collecting team playoff win count " + str(counter) + "/" + str(len(team_seasons)))
    counter += 1

playoff_win_data = pd.DataFrame({"TEAM_ID": team_seasons["TEAM_ID"], "SEASON": team_seasons["YEAR"], "NUM_PLAYOFF_WINS":num_playoff_wins})
playoff_win_data.to_sql("TEAM_SEASON_PLAYOFF_WINS", engine, if_exists="replace", index=False)
    

