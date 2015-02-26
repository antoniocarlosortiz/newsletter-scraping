import urllib2 as request
from bs4 import BeautifulSoup
import re
from pprint import pprint
import subprocess


base_url = 'http://espn.go.com'

teams_url = 'http://espn.go.com/nba/teams'
html_teams = request.urlopen(teams_url)
soup_teams = BeautifulSoup(html_teams)

urls = soup_teams.find_all(href = re.compile('/nba/teams/stats'))
team_urls = [base_url+url['href'] for url in urls]

team_name_dict = {'bos':'Boston Celtics',
                  'bkn':'Brooklyn Nets',
                  'nyk':'New York Knicks',
                  'phi':'Philadelphia 76ers',
                  'tor':'Toronto Raptors',
                  'gsw':'Golden State Warriors',
                  'lac':'Los Angeles Clippers',
                  'lal':'Los Angeles Lakers',
                  'pho':'Phoenix Suns',
                  'sac':'Sacramento Kings',
                  'chi':'Chicago Bulls',
                  'cle':'Cleveland Cavaliers',
                  'det':'Detroit Pistons',
                  'ind':'Indiana Pacers',
                  'mil':'Milwaukee Bucks',
                  'dal':'Dallas Mavericks',
                  'hou':'Houston Rockets',
                  'mem':'Memphis Grizzlies',
                  'nor':'New Orleans Pelicans',
                  'sas':'San Antonio Spurs',
                  'atl':'Atlanta Hawks',
                  'cha':'Charlotte Hornets',
                  'mia':'Miami Heat',
                  'orl':'Orlando Magic',
                  'was':'Washington Wizards',
                  'den':'Denver Nuggets',
                  'min':'Minnesota Timberwolves',
                  'okc':'Oklahoma City Thunder',
                  'por':'Portland Trail Blazers',
                  'uth':'Utah Jazz'
                  }

url_team = 'http://espn.go.com/nba/teams/stats?team=cle'
team_code = url_team[-3:]

html_team = request.urlopen(url_team)
soup_team = BeautifulSoup(html_team)

#Grab all HTML tr elements with class containing the word 'player'
#returns objects
roster = soup_team.find_all('tr', class_=re.compile('player'))

#Grab the top half of the data, which contains the game stats
roster_game_stats = roster[:int(len(roster)/2)]

#Grab the bottom half of the data, which contains the shooting stats
roster_shooting_stats = roster[-int(len(roster)/2):]

players = []
for row in roster_game_stats:
	for data in row:
		players.append(data.get_text())

# 7 on split because there are seven '/' on the href
player_ids = [player.a['href'].split('/')[7] for player in roster_game_stats]

index = 0
increment = 0
for id in player_ids:
	players.insert(index + increment, id)
	index = index + 15
	increment = increment + 1

index = 2
increment = 0
for id in player_ids:
	players.insert(index + increment, team_name_dict[team_code])
	index = index + 16 # since we added player ID, there is now a total of 16 columns, instead of 15.
	increment = increment + 1

def chunks(l,n):
	""" Yield successive n-sized chunks from l.
	"""
	for i in range(0, len(l), n):
		yield l[i:i+n]

from pprint import pprint

for row in chunks(players, 17):
	pprint(row)

