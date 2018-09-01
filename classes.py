from collections import OrderedDict


class club():
    # class for each club team

    def __init__(self, alias):
        self.elo_score = 1500
        self.elo_history = []
        self.alias = alias
    
class team_dict():

    def __init__(self):
        self.teams = {}
        
    def update(self, schedule):
        for team in set(schedule.df.Home_Team):
            if team not in self.teams.keys():
                self.teams[team] = club(team)

class game():
    # pass in two club objects and the scores

    def __init__(self, home_club, away_club, home_score, away_score):
        score_factor = 25
        self.home = home_club
        self.away = away_club
        self.home_score = int(home_score)
        self.away_score = int(away_score)
        if self.home_score == self.away_score:
            self.winner = home_club if home_club.elo_score < away_club.elo_score else away_club
        else if self.home_score > self.away_score:
            self.winner = home_club
        else:
            self.winner = away_club
        
        self.loser = away_club if self.winner == home_club else home_club
        self.point_diff = abs(self.home_score - self.away_score)
        self.spread = (self.home.elo_score - self.away.elo_score)/score_factor
        self.prediction = 1 / (10 ** (-(self.home.elo_score - self.away.elo_score)/400) + 1)
        self.elo_change = (np.log(self.point_diff  + 1)) * score_factor


class schedule():

    def __init__(self, year, source_df):
        self.year = year
        self.df = source_df.sort_values(by = 'Week')

    def make_games(self, all_teams):
        self.games = OrderedDict()
        for elem in self.df.iterrows():
            row = elem[1]
            self.games[str(row["Home_Team"]) + "__" + str(row["Away_Team"])] = game(all_teams.teams[row['Home_Team']], all_teams.teams[row['Away_Team']], row['Home_Score'], row['Away_Score'])
