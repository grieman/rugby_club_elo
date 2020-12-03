import bs4
from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import re
import random
import datetime
import itertools
import csv

#from classes import club, team_dict, game, schedule
#from Club_Name_Mapping import name_mappings

name_mappings = {
    'Bath': ['Bath Rugby'],
    'Bristol': ['Bristol Rugby'],
    'Gloucester': ['Gloucester RFC'],
    'Leicester': ['Leicester Tigers']
}

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

def read_1993_table(url):
    session = requests.session()
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    scores = soup.find_all('table')[3]
    rows = scores.find_all('tr')
    all_scores = []
    for i in range(1, len(rows)):
        by_club = [rows[i].find_all('td')[0].contents[0].contents[0]]
        scores = rows[i].find_all('td')
        for j in range(1, len(scores)):
            score = scores[j].contents[0].rstrip().replace(chr(8211), '-')
            by_club.append(score)
        all_scores.append(by_club)

    scores_df = pd.DataFrame(all_scores)
    club_names = ['Clubs']
    club_names.extend(list(scores_df[0]))
    scores_df.columns = club_names
    return(scores_df)

def get_match_scores(url, year):
    if (year < 1993):
        scores_df = read_old_table(url)
    elif (year < 1997):
        scores_df = read_1993_table(url)

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

## GET FIRST BATCH, TO 1993
for year in range(1987, 1997):
    url = "https://en.wikipedia.org/wiki/" + str(year) + "-" + str(year - 1899) + "_Courage_League#Results"
    df = get_match_scores(url, year)
    #missing dates for most games - they will be put into a random order
    weeks = random.sample(list(range(df.shape[0])), df.shape[0])
    if (year == 1987): # From http://www.ipernews.com/RUGBY/guinness_19871988.htm
        weeks = [8, 27, 3, 100, 15, 4, 15, 9, 7, 13, 29, 24, 5, 30,
                               4, 18, 14, 2, 17, 9, 28, 19, 30, 13, 4, 26, 18, 29,
                               21, 2, 16, 6, 25, 13, 27, 9, 22, 14, 7, 18, 29, 7,
                               100, 12, 1, 100, 12, 24, 20, 11, 100, 30, 6, 2, 23,
                               12, 28, 17, 14, 29, 10, 8, 17, 26]
    weeks = [datetime.timedelta(days=week) for week in weeks]
    dates = [datetime.datetime.strptime(str(year) + '0901', '%Y%m%d').date()]
    dates = [date + offset for date, offset in zip(itertools.cycle(dates), weeks)]
    # September 1, year + df["Week"] days
    df['Date'] = dates     
    #for club in name_mappings:
    #    df = df.replace(name_mappings[club], club)

    df.to_csv('Premiership_Tables/English_Premiership_'+ str(year) +'.csv')



for year in range(1997, 2020):
    if (year == 1999):
        url = "https://en.wikipedia.org/wiki/" + str(year) + "-" + str(2000) + "_Premiership_Rugby#Fixtures"
    elif (year >= 2010):
        url = url = "https://en.wikipedia.org/wiki/" + str(year) + "-" + str(year - 1999) + "_Premiership_Rugby#Regular_season"
    elif (year == 2009):
        url = "https://en.wikipedia.org/wiki/" + str(year) + "-" + str(year - 1999) + "_Premiership_Rugby#Fixtures"
    elif (year > 1999):
        url = "https://en.wikipedia.org/wiki/" + str(year) + "-0" + str(year - 1999) + "_Premiership_Rugby#Fixtures"
    else:
        url = "https://en.wikipedia.org/wiki/" + str(year) + "-" + str(year - 1899) + "_Premiership_Rugby#Fixtures"

    session = requests.session()
    response = session.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    rows = soup.find_all('table')

    #if (year >= 2010):
    #    rows = rows[3:len(rows)]
    #else:
    end = next(i for i in range(3, len(rows)) if str(rows[i])[0:23] == '<table class="wikitable')
    rows = rows[3:end]
    
    ## Remove rows with tables that we don't want
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table width="100%">']
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table cellpadding="']
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table align="center']
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table class="mbox-s']
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table border="0" ce']
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table class="multic']
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table style="width:']
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table style="font-s']
    rows = [rows[i] for i in range(0, len(rows)) if str(rows[i])[0:20] != '<table style="border']

    dates = [rows[i].find('td').find('div').contents[0] for i in range(0, len(rows),3)]
    dates = [x.contents[0] if len(x) == 1 else x for x in dates] ## removes links in dates, like Big Game


    home_team = []
    home_score = []
    away_score = []
    away_team = []
    for i in range(1, len(rows), 3):
        content = rows[i].find_all('th')
        if (str(content[1].contents[0])[0:8] == '<a href='):
            ## If there is a link, not a score
            scores = [-1, -1]
        else:
            scores = content[1].contents[0].split('\n',1)[0]#.replace('–','-').split('-',1)
            scores = re.sub("[^0-9]", " ", scores)
            scores = [int(s) for s in scores.split() if s.isdigit()]
            if len(scores) == 0:
                ## If the score field has something like P-P
                scores =  [-1, -1]

        ## NEED TO ENSURE GETTING TEAM NAME
        try:
            home = content[0].contents[0].contents[0].contents[0]
            if((str(home) == '(BP)')|(str(home) == '(1 BP)')|(str(home) == '(2 BP)')|(str(home) == '(BP) ')|(str(home) == '(1 BP) ')|(str(home) == '(2 BP) ')):
                ## Look in secondary location if bonus points are here
                home = content[0].contents[0].contents[2].contents[0]
        except:
            home = content[0].contents[0].contents[0]
            if((str(home) == '(BP)')|(str(home) == '(1 BP)')|(str(home) == '(2 BP)')|(str(home) == '(BP) ')|(str(home) == '(1 BP) ')|(str(home) == '(2 BP) ')):
                home = content[0].contents[0].contents[1].contents[0]

        try:
            away = content[2].contents[0].contents[0].contents[0]
            if (str(away)[0:20] == '<a href="/wiki/Engla'):
                away = content[2].contents[0].contents[2].contents[0]
        except:
            away = content[2].contents[0].contents[0]
            if (str(away)[0] == "("):
                away = content[2].contents[0].contents[1].contents[0]
        
        ## Get the first score element for home, and second for away
        try:
            score_h = scores[0][0]
        except:
            score_h = scores[0]

        try:
            score_a = scores[1][0]
        except:
            score_a = scores[1]

        # Clean the names and append
        home = re.sub("\(.*\)|\s-\s.*", "", home)
        away = re.sub("\(.*\)|\s-\s.*", "", away)
        home_score.append(score_h)
        away_score.append(score_a)
        home_team.append(home)
        away_team.append(away)
    
    df = pd.DataFrame({'Away_Score':away_score, 'Away_Team':away_team, 'Home_Score':home_score, 'Home_Team':home_team, "Date":dates})
    df = df[(df.Away_Score != -1) & (df.Home_Score != -1)]
    df.to_csv('Premiership_Tables/English_Premiership_'+ str(year) +'.csv')





