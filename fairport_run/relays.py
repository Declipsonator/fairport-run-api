import heapq

from fairport_run.utils import format_time


class Relay(object):
    relays = []

    def __init__(self, athletes, *events):
        """
        athletes: dict mapping athlete_id -> { ..., "performances": { event: {"performance": raw_time}, ... } }
        events: sequence of event names (may contain duplicates, e.g. ("200m","200m","800m","400m"))
        """
        self.athletes = athletes
        self.events = list(events)
        # dedupe for building top_marks
        diff_events = set(events)

        # build sorted mapping event -> { time (float) -> athlete_id }
        top = {}
        for ev in diff_events:
            marks = {}
            for athid, data in athletes.items():
                perf = data["performances"].get(ev)
                if perf is not None:
                    t = format_time(perf["performance"])
                    marks[t] = athid
            # sort by time ascending
            top[ev] = dict(sorted(marks.items()))
        self.top_marks = top

    def generate_relays(self, number):
        n = len(self.events)
        legs_lists = [list(self.top_marks[e].items()) for e in self.events]

        # Failsafe: ensure enough entries per event
        from collections import Counter
        event_counts = Counter(self.events)
        for ev, count in event_counts.items():
            available_athletes = len(self.top_marks.get(ev, {}))
            if available_athletes < count:
                self.relays =  []  # Not enough unique athletes for this event

        # Additional check: make sure all legs_lists are non-empty
        if any(len(leg_list) == 0 for leg_list in legs_lists):
            self.relays = []

        event_groups = {
            ev: [i for i, e in enumerate(self.events) if e == ev]
            for ev in set(self.events)
        }

        def is_sorted_for_duplicates(idx_tuple, dim):
            ev = self.events[dim]
            grp = event_groups[ev]
            vals = [idx_tuple[i] for i in grp]
            return all(vals[i] <= vals[i + 1] for i in range(len(vals) - 1))

        start = (0,) * n
        heap = []
        visited = {start}
        t0 = sum(legs_lists[i][0][0] for i in range(n))
        heapq.heappush(heap, (t0, start))

        results = []
        while heap and len(results) < number:
            total, idx = heapq.heappop(heap)
            athlete_ids = [legs_lists[i][idx[i]][1] for i in range(n)]
            if len(set(athlete_ids)) == n:
                legs = [
                    {
                        "event": self.events[i],
                        "athlete_id": athlete_ids[i],
                        "time": legs_lists[i][idx[i]][0],
                    }
                    for i in range(n)
                ]
                results.append({"time": format_time(round(total, 2)), "legs": legs})

            for d in range(n):
                i2 = idx[d] + 1
                if i2 < len(legs_lists[d]):
                    new_idx = list(idx)
                    new_idx[d] = i2
                    new_idx = tuple(new_idx)
                    if new_idx in visited:
                        continue
                    if not is_sorted_for_duplicates(new_idx, d):
                        continue
                    new_total = total - legs_lists[d][idx[d]][0] + legs_lists[d][i2][0]
                    visited.add(new_idx)
                    heapq.heappush(heap, (new_total, new_idx))

        self.relays = results



