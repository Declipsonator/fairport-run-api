import datetime
import requests
import json

import purdy
from performanceutils import format_time, event_to_dist

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
        self.data = self.get_array()
        self.athletes = self.organize_data()

    def organize_data(self):
        """Organizes an array of athletes' performances into a dictionary"""
        organized_data = {}
        team_relays = {}

        for performance in self.data:
            ath_id = performance['athlete_id']
            if ath_id not in organized_data.keys():
                organized_data[performance['athlete_id']] = {
                    'name': f'{performance["athlete_fname"]} {performance["athlete_lname"]}',
                    'team': performance['team_name'],
                    'grade': (self.year + 12) - int(performance['graduate']),
                    'performances': {}
                }

            organized_data[ath_id]['performances'][performance['event_name']] = {
                'performance': performance['performance'],
                'date': performance['meet_date'],
                'meet': performance['meet'],
                'type': 'track' if performance['tf'] == 'T' else 'field',
                'fat': (int(performance['resultType']) == 0),
                'converted': False,
                'converted_from': None
            }

        return organized_data




    def get_array(self):
        """Returns an array containing all athletes of the specific team's top performance in each event"""
        page = 0
        has_next = True
        data = []

        events = list(json.loads(requests.get('https://www.yentiming.com/results2/getEvents').text)[self.season].keys())
        url = f'https://www.yentiming.com/leaderboard/get?limit=49&sex={self.gender}&teams[]={self.team}&season={self.season}&year={self.year}'
        events_query = '&'.join([f'events[]={event}' for event in events])
        url = f'{url}&{events_query}'

        while has_next:
            page += 1
            response = requests.get(f'{url}&page={page}').text
            info = json.loads(json.loads(response))
            has_next = info['hasNext']
            data += info['results']

        return data


    def add_converted(self, event_to, *event_from):
        """Converts similar events to a single event using purdy point conversion

        Args:
            event_to: The event to convert to and add to the array
            event_from: The events to convert from
        """

        event_from = list(event_from)
        event_from.append(event_to)


        for athlete_id in self.athletes.keys():
            lowest_time = -1
            converted_from = None
            for event in self.athletes[athlete_id]["performances"].keys():
                if event in event_from:
                    conversion = (purdy.Purdy(event_to_dist(event),
                                             format_time(self.athletes[athlete_id]["performances"][event]["performance"]))
                                            .convert(event_to_dist(event_to)))
                    if conversion < lowest_time or lowest_time == -1:
                        lowest_time = conversion
                        converted_from = event

            if converted_from and converted_from != event_to:
                self.athletes[athlete_id]["performances"][event_to] = {
                    'performance': format_time(lowest_time),
                    'date': None,
                    'meet': None,
                    'type': 'track',
                    'fat': self.athletes[athlete_id]['performances'][converted_from]['fat'],
                    'converted': True,
                    'converted_from': converted_from
                }

    def add_indoor_conversions(self):
        self.add_converted('200m', '300m')
        self.add_converted('400m', '300m', '600m')
        self.add_converted('800m', '600m', '1000m')
        self.add_converted('1200m', '1000m', '1600m')
        self.add_converted('1600m', '1500m')
        self.add_converted('1609.3m', '1600m', '1500m')

    def add_outdoor_conversions(self):
        self.add_converted('1200m', '1600m')
        self.add_converted('1600m', '1500m')
        self.add_converted('1609.3m', '1600m', '1500m')






# yen = YenData(season='indoor', year=2025)
# yen.add_indoor_conversions()
# print(json.dumps(yen.athletes))

