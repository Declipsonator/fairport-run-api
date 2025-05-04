import json
import os
import time
from datetime import datetime

from fastapi import FastAPI, HTTPException

from performanceutils import get_current_season, get_current_year
from yendata import YenData

app = FastAPI()

@app.get("/")
def read_root():
    return {"Info": "This is the root directory of the Fairport.run API. View /docs for more information."}

@app.get("/athletes/{year}/{season}")
def read_athletes(year: int, season: str):
    """## Returns a list of athletes and their top performance in each event

    Args:\n
        year (int): The year of the season\n
        season (int): The season of track
    """

    if season != 'indoor' and season != 'outdoor':
        raise HTTPException(status_code=404)

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


def get_file_age(file_path):
    """
    Calculates the age of a file in seconds.

    Args:
      file_path: The path to the file.

    Returns:
      The age of the file in seconds, or None if the file does not exist.
    """
    if not os.path.exists(file_path):
        return None

    # Get the file's modification timestamp
    modification_timestamp = os.path.getmtime(file_path)

    # Calculate the file age by subtracting the modification timestamp from the current timestamp
    file_age = time.time() - modification_timestamp
    return file_age


def get_athletes(year, season):
    yen = YenData(year=year, season=season)
    yen.add_converted()
    yen.save_athletes()







