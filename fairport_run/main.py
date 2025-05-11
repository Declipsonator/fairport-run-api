import json
import os
from datetime import datetime
from enum import Enum
from typing import List

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from fairport_run.relays import Relay
from fairport_run.utils import get_current_season, get_current_year, get_file_age
from fairport_run.yendata import YenData

app = FastAPI()

origins = [
    "https://alpha.fairport.run",
    "https://fairport.run",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # use ["*"] for public APIs (not recommended for private APIs)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class RelayRequest(BaseModel):
    year: int
    season: str
    gender: str
    legs: List[str]

@app.get("/")
def read_root():
    return {"Info": "This is the root directory of the Fairport.run API. View /docs for more information."}

@app.get("/athletes/{year}/{season}/{gender}")
def read_athletes(year: int, season: str, gender: str):
    """## Returns a list of athletes and their top performance in each event

    Args:\n
        year (int): The year of the season\n
        season (str): The season of track 'indoor' or 'outdoor'
        gender (str): The gender 'm' or 'f'
    """

    if os.path.exists(f'{season}/{gender}/{year}.json'):
        if season == get_current_season() and year == get_current_year() and get_file_age(f'{season}/{gender}/{year}.json') > 60 * 60 * 12:
            get_athletes(year, season, gender)
            return read_athletes(year, season, gender)


        with open(f'{season}/{gender}/{year}.json', 'r') as f:
            return json.load(f)
    else:
        now = datetime.now()

        if year < 2008 or year > now.year + 1:
            raise HTTPException(status_code=404)

        get_athletes(year, season, gender)
        return read_athletes(year, season, gender)

@app.post("/relays")
def relays(request: RelayRequest):
    """Returns a list of the 10 fastest possible relays in a given year

    Args:\n
        year (int): The year of the season
        season (str): The season of track
        legs (tuple): The legs of the race
        gender (str): The gender 'm' or 'f'
    """

    athletes = read_athletes(request.year, request.season, request.gender)
    relay = Relay(athletes, *request.legs)
    relay.generate_relays(10)
    return relay.relays

@app.get("/years")
def years():
    """Returns a list of all possible years"""
    return list(range(2008, get_current_year() + 1))




def get_athletes(year, season, gender):
    """Fetches the results of the season from yentiming and then saves them

    Args:
        year (int): The year of the season.
        season (str): The season, 'indoor' or 'outdoor'.
    """
    yen = YenData(year=year, season=season, gender=gender)
    yen.add_converted()
    yen.save_athletes()