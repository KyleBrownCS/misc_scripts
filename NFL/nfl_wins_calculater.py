import urllib.request
import json
from datetime import timedelta, datetime

def get_leaders(a,b):
    players = {
        "NAT":  ["SEA", "CIN", "CAR", "SF"],
        "Bags": ["NE", "WAS", "MIN", "JAX"],
        "Fowl": ["GB", "TEN", "PHI", "DET"],
        "Trev": ["PIT", "OAK", "HOU", "MIA"],
        "JT":   ["KC", "ARI", "DEN", "LAC"],
        "KBr":  ["ATL", "DAL", "BAL", "NO"],
        "Brett": ["TB", "NYG", "BUF", "IND"]
    }

    # prep players
    player_details = {}
    for name in players.keys():
        player_details[name] = {}
        player_details[name]["wins"] = 0
        player_details[name]["points"] = 0
        player_details[name]["games_remain"] = 0

    # generate/retreive all game details
    r = urllib.request.urlopen("https://sports.yahoo.com/site/api/resource/sports.league.standings;alias=mini_standings;combineGroups=;conference=;count=100;division=;league=nfl;leagueSeason=standings;season=;seasonPeriod=;topDivisionOnly=?bkt=spdmtest&device=desktop&feature=canvassOffnet%2CnewContentAttribution%2Clivecoverage%2Ccanvass&intl=us&lang=en-US&partner=none&prid=3hcrun1cre6dd&region=US&site=sports&tz=America%2FWinnipeg&ver=1.0.1954&returnMeta=true")
    web_data =  json.loads(r.read())

    teams = web_data['data']['teams']
    results = web_data['data']['teamteam_standing']

    team_names = {}
    team_details = {}
    for team, data in teams.items():

        team_names[data['team_id']] = data['abbr']  # eg. t2.nfl5 = NYG

        team_details[team_names[data['team_id']]] = {}
        team_details[team_names[data['team_id']]]["wins"] = 0
        team_details[team_names[data['team_id']]]["points"] = 0
        team_details[team_names[data['team_id']]]["games_remain"] = 0


    for team, result in results.items():
        team_details[team_names[team]]["wins"] = int(result["team_record"]["wins"])
        team_details[team_names[team]]["points"] = int(result["points_for"])
        team_details[team_names[team]]["games_remain"] = 16 - int(result["team_record"]["played"])


    for name, teams in players.items():
        for team in teams:
            player_details[name]["wins"] += team_details[team]["wins"]
            player_details[name]["points"] += team_details[team]["points"]
            player_details[name]["games_remain"] += team_details[team]["games_remain"]


    leaders = sorted(player_details.items(), key=lambda k: (k[1]["wins"], k[1]["points"], k[1]["games_remain"]))
    leaders.reverse()


    final_print = "Name    Wins      Points    Games Remaining\r\n"

    for leader in leaders:
        final_print += str(leader[0]).ljust(8) + str(leader[1]["wins"]).ljust(10) + str(leader[1]["points"]).ljust(15) +str(leader[1]["games_remain"]).ljust(10) + "\r\n"

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": str(final_print)
    }


if __name__ == "__main__":
    print (get_leaders(0,0))