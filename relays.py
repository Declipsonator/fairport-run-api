import math

from performanceutils import format_time


class Relay(object):
    relays = []


    def __init__(self, athletes, *events):
        """Takes a dictionary produced by yendata and formulates a sorted array of relays with the events provided.

        Args:
            athletes (dict): A dictionary produced by yendata
            events: All the events in the relay
        """

        diff_events = list(set(events))
        self.diff_events = diff_events
        self.athletes = athletes
        self.events = events
        top_marks = {}

        for event in diff_events:
            top_marks[event] = {}
            for index, (athid, athlete) in enumerate(athletes.items()):
                if event in athlete["performances"].keys():
                    top_marks[event][format_time(athlete["performances"][event]["performance"])] = athid

            top_marks[event] = dict(sorted(top_marks[event].items()))

        self.top_marks = top_marks

    def generate_relays(self, number):
        self.relays = []  # Clear relays at the start

        for event in self.diff_events:
            if len(self.top_marks[event]) < 4:
                return  # Exit if any event has fewer than 4 performances

        if len(self.diff_events) == 1:
            # Single event case
            event = self.diff_events[0]
            possible_relays = min(math.comb(len(self.top_marks[event]), 4), number)
            times = list(self.top_marks[event].items())

            for i in range(possible_relays):
                team = times[i * 4:(i + 1) * 4]
                if len(team) < 4:
                    break
                time = sum(float(time) for time, _ in team)
                self.relays.append({
                    'team': [athid for _, athid in team],
                    'time': time
                })
        else:
            # TODO: Multi-event relays (Ex. DMR)
            pass



# yen = YenData(testing=True)
# relay = Relay(yen.athletes, "200m", "200m", "200m", "200m")
# print(relay.top_marks)
# relay.generate_relays(10)
# print(relay.relays)



