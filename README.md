# Fairport Run Data API
## Overview
This repository contains the python scripts that collect and aggregate data from Fairport's runners.
The data is then served through an api defined in `main.py`. The frontend can be viewed in https://github.com/declipsonator/fairport-run-frontend
## Data Collection
Most of the data is collected through the https://yentiming.com api which is not publicly available and had to be reverse engineered.
## Running
`uvicorn fairport_run.main:app --reload`