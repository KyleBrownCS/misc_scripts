import urllib.request
import json
from datetime import timedelta, datetime


players = {
    "Nat":  ["SEA", "CIN", "CAR", "SF"],
    "Bags": ["NE", "WAS", "MIN", "JAX"],
    "Fowl": ["GB", "TEN", "PHI", "DET"],
    "Trev": ["PIT", "OAK", "HOU", "MIA"],
    "JT":   ["KC", "ARI", "DEN", "LAC"],
    "KBr":  ["ATL", "DAL", "BAL", "NO"],
    "Brad": ["TB", "NYG", "BUF", "IND"]
}
def _get_total_records(records):
    """This will take a list of string records and will add them all together and return the results"""
    result = ""
    wins = 0
    losses = 0
    ties = 0

    for record in records:
        win, loss, tie = record.split("-")

        wins += int(win)
        losses += int(loss)
        ties += int(ties)


    return str(wins) + "-" + str(losses) + "-" + str(ties)


def _generate_extra_details(team_details, player_details):
    """This will give a more verbose view of each players teams record and stats"""

    intro = "        record  W  L  pts  pts_agst  rem\r\n"
    output = ""

    """
        team_details[team_names[data['team_id']]] = {}
        team_details[team_names[data['team_id']]]["wins"] = 0
        team_details[team_names[data['team_id']]]["losses"] = 0
        team_details[team_names[data['team_id']]]["points"] = 0
        team_details[team_names[data['team_id']]]["record"] = "N/A"
        team_details[team_names[data['team_id']]]["games_remain"] = 0
    """

    for name, teams in players.items():
        output += intro
        output += name + "\r\n"
        records = []
        for team in teams:
            output += team.rjust(6)
            output += team_details[team]["record"].rjust(8)

            records.append(team_details[team]["record"])

            output += str(team_details[team]["wins"]).rjust(3)
            output += str(team_details[team]["losses"]).rjust(3)
            output += str(team_details[team]["points_for"]).rjust(5)
            output += str(team_details[team]["points_against"]).rjust(10)
            output += str(team_details[team]["games_remain"]).rjust(5)
            output += "\r\n"

        # add totals

        # this is a magic line of ='s the length of the intro and shifted to be inline
        output += (len(intro.lstrip()[:-2]) * "=").rjust(len(intro[:-2]))
        output += "\r\n"

        output += _get_total_records(records).rjust(14)
        output += str(player_details[name]["wins"]).rjust(3)
        output += str(player_details[name]["losses"]).rjust(3)
        output += str(player_details[name]["points_for"]).rjust(5)
        output += str(player_details[name]["points_against"]).rjust(10)
        output += str(player_details[name]["games_remain"]).rjust(5)
        output += "\r\n"
        output += "\r\n"

    return output

def _generate_output(players_stats):
    """Takes a list of players and their total teams stats and transforms the data into a nice print out."""

    # sort by wins, then points then remaining games
    leaders = sorted(players_stats.items(), key=lambda k: (k[1]["wins"], k[1]["points_for"], k[1]["games_remain"]))
    leaders.reverse()

    #manage output
    final_print = "  Name  wins  points  games_remaining\r\n"

    for leader in leaders:
        final_print += str(leader[0]).rjust(6)
        final_print += str(leader[1]["wins"]).rjust(6)
        final_print += str(leader[1]["points_for"]).rjust(8)
        final_print += str(leader[1]["games_remain"]).rjust(17)
        final_print += "\r\n"

    return final_print


def get_leaders(event, context):

    # prep players
    player_details = {}
    for name in players.keys():
        player_details[name] = {}
        player_details[name]["wins"] = 0
        player_details[name]["losses"] = 0
        player_details[name]["points_for"] = 0
        player_details[name]["points_against"] = 0
        player_details[name]["games_remain"] = 0

    # generate/retreive all game details
    r = urllib.request.urlopen("https://sports.yahoo.com/site/api/resource/sports.league.standings;alias=mini_standings;league=nfl;leagueSeason=standings;")
    web_data =  json.loads(r.read())

    teams = web_data['teams']                # team names only
    results = web_data['teamteam_standing']  # standings for teams

    team_names = {}     # contains the weird t2.nfl15 = NYG pairings. 
    team_details = {}   # full teams details

    # init all the things
    for team, data in teams.items():

        team_names[data['team_id']] = data['abbr']  # eg. t2.nfl5 = NYG

        team_details[team_names[data['team_id']]] = {}
        team_details[team_names[data['team_id']]]["wins"] = 0
        team_details[team_names[data['team_id']]]["losses"] = 0
        team_details[team_names[data['team_id']]]["points_for"] = 0
        team_details[team_names[data['team_id']]]["points_against"] = 0
        team_details[team_names[data['team_id']]]["record"] = "N/A"
        team_details[team_names[data['team_id']]]["games_remain"] = 0

    # Grab all the relevant information
    for team, result in results.items():
        team_details[team_names[team]]["wins"] = int(result["team_record"]["wins"])
        team_details[team_names[team]]["losses"] = int(result["team_record"]["losses"])
        team_details[team_names[team]]["record"] = result["team_record"]["display"]
        team_details[team_names[team]]["points_for"] = int(result["points_for"])
        team_details[team_names[team]]["points_against"] = int(result["points_against"])
        team_details[team_names[team]]["games_remain"] = 16 - int(result["team_record"]["played"])

    # Generate each players stats based on the teams they own
    for name, teams in players.items():
        for team in teams:
            player_details[name]["wins"] += team_details[team]["wins"]
            player_details[name]["losses"] += team_details[team]["losses"]
            player_details[name]["points_for"] += team_details[team]["points_for"]
            player_details[name]["points_against"] += team_details[team]["points_against"]
            player_details[name]["games_remain"] += team_details[team]["games_remain"]


    return_text = _generate_output(player_details) +"\r\n\r\n" +  _generate_extra_details(team_details, player_details)

    return {
        "isBase64Encoded": False,
        "statusCode": 200,
        "body": str(return_text)
    }


if __name__ == "__main__":
    print (get_leaders(None,None)["body"].replace("\r\n", "\n"))
