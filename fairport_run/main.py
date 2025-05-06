import json
import os
from datetime import datetime
from enum import Enum
from typing import List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from fairport_run.relays import Relay
from fairport_run.utils import get_current_season, get_current_year, get_file_age
from fairport_run.yendata import YenData

app = FastAPI()

class RelayRequest(BaseModel):
    year: int
    season: str
    legs: List[str]  # or List[float] or whatever type legs actually are

@app.get("/")
def read_root():
    return {"Info": "This is the root directory of the Fairport.run API. View /docs for more information."}

@app.get("/athletes/{year}/{season}")
def read_athletes(year: int, season: str):
    """## Returns a list of athletes and their top performance in each event

    Args:\n
        year (int): The year of the season\n
        season (str): The season of track
    """

    if os.path.exists(f'{season}/{year}.json'):
        if season == get_current_season() and year == get_current_year() and get_file_age(f'{season}/{year}.json') > 60 * 60 * 12:
            get_athletes(year, season)
            return read_athletes(year, season)


        with open(f'{season}/{year}.json', 'r') as f:
            return json.load(f)
    else:
        now = datetime.now()

        if year < 2008 or year > now.year + 1:
            raise HTTPException(status_code=404)

        get_athletes(year, season)
        return read_athletes(year, season)

@app.post("/relays")
def relays(request: RelayRequest):
    """Returns a list of the 10 fastest possible relays in a given year

    Args:\n
        year (int): The year of the season
        season (str): The season of track
        legs (tuple): The legs of the race
    """

    athletes = read_athletes(request.year, request.season)
    relay = Relay(athletes, *request.legs)
    relay.generate_relays(10)
    return relay.relays

@app.get("/years")
def years():
    """Returns a list of all possible years"""
    return list(range(2008, get_current_year() + 1))




def get_athletes(year, season):
    """Fetches the results of the season from yentiming and then saves them

    Args:
        year (int): The year of the season.
        season (str): The season, 'indoor' or 'outdoor'.
    """
    yen = YenData(year=year, season=season)
    yen.add_converted()
    yen.save_athletes()