import bs4
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re

url = "https://en.wikipedia.org/wiki/1987-88_Courage_League#Results"
session = requests.session()
response = session.get(url)
soup = BeautifulSoup(response.content, "html.parser")


def read_old_table(url):
    session = requests.session()
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    scores = soup.find_all('table')[3]
    rows = scores.find_all('tr')

    #club_names = []
    #for name in rows[0].find_all('th'):
    #   club = name.contents[0].rstrip()
    #    club_names.append(club)

    all_scores = []
    for i in range(1, len(rows)):
        by_club = [rows[i].find_all('th')[0].contents[0].contents[0]]
        scores = rows[i].find_all('td')
        for j in range(len(scores)):
            score = scores[j].contents[0].rstrip().replace(chr(8211), '-')
            by_club.append(score)
        all_scores.append(by_club)

    scores_df = pd.DataFrame(all_scores)
    club_names = ['Clubs']
    club_names.extend(list(scores_df[0]))
    scores_df.columns = club_names
    return(scores_df)

def get_match_scores(read_df):
    parsed_matches = pd.DataFrame()
    for index, row in scores_df.iterrows():
        home_club = row[0]
        for i in range(1, len(row)):
            if len(row[i]) > 0:
                home_score, away_score = row[i].split('-')
                away_team = scores_df.columns[i]
                match_record = {'Home_Team':home_club, 'Home_Score':home_score, 'Away_Score':away_score, 'Away_Team':away_team}
                parsed_matches = parsed_matches.append(pd.DataFrame(match_record, index=[0]), ignore_index=True)

    return(parsed_matches)

scores_df = read_old_table(url)
match_scores = get_match_scores(scores_df)
# FROM http://www.ipernews.com/RUGBY/guinness_19871988.htm, 4 games had no dates and are here 100 to be at the end of the season
match_scores["Week"] = [8, 27, 3, 100, 15, 4, 15, 9, 7, 13, 29, 24, 5, 30, 4, 18, 14, 2, 17, 9, 28, 19, 30, 13, 4, 26, 18, 29, 21, 2, 16, 6, 25, 13, 27, 9, 22, 14, 7, 18, 29, 7, 100, 12, 1, 100, 12, 24, 20, 11, 100, 30, 6, 2, 23, 12, 28, 17, 14, 29, 10, 8, 17, 26]



### ELO
# margin of victory: np.log(MOV) + 1 * K to get score change
# Pr(A) = 1 / 10^(-ELODIFF/400) + 1
# multiplier: (Margin of Victory + some win score(3))^.8 / 7.5 * .006(ELO DIFF)    
# K * (1 - wn probablity) * Margin of victory multiplier = ~+2.39.


all_teams = team_dict()
year_1 = schedule('1', match_scores)
all_teams.update(year_1)
year_1.make_games(all_teams)


for name, match in year_1.games.items():
    match.process_game()

for club in all_teams.teams.values():
    print(club.elo_history)