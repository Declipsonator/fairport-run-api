import datetime
import requests
import json

class YenData(object):

    def __init__(self, season='', year=0, gender='m', team=85):
        """A class to collect, organize and save running data from yentiming.com

        Args:
            season: 'indoor' or 'outdoor'
            year: the year of the season
            gender: 'm' or 'f'
            team: the id of the team (can be obtained from https://www.yentiming.com/results2/getTeams)
        """

        now = datetime.datetime.now()
        month = now.month

        # If season is not defined, we choose indoor between November and March and outdoor between April and October
        self.season = season if season else ('indoor' if month < 4 or month > 10 else 'outdoor')
        # If year is not defined, we choose the current year if the month is before November and the next year otherwise (because the season is indoor)
        self.year = year if year else (now.year if month < 11 else now.year + 1)
        self.gender = gender
        self.team = team

    def collect_data(self):
        """Collects and organizes all athletes of a specific team from the yentiming database"""


    def get_array(self):
        """Returns an array containing all athletes of the specific team's top performance in each event"""
        page = 0
        has_next = True
        data = []

        events = list(json.loads(requests.get('https://www.yentiming.com/results2/getEvents').text)[self.season].keys())
        url = f"https://www.yentiming.com/leaderboard/get?limit=49&sex={self.gender}&teams[]={self.team}&season={self.season}&year={self.year}"
        events_query = "&".join([f"events[]={event}" for event in events])
        url = f"{url}&{events_query}"

        while has_next:
            page += 1
            response = requests.get(f"{url}&page={page}").text
            info = json.loads(json.loads(response))
            has_next = info['hasNext']
            data += info['results']

        return data

