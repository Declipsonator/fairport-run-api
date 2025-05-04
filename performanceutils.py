from datetime import datetime

def format_time(time):
    """Formats floats into time strings and time strings into floats.
    Args:
        time (float or str): Time in seconds or a string in the format "MM:SS" or "MM:SS.sss".
    """

    if isinstance(time, str):
        time = time.split(":")
        minutes = int(time[0])
        seconds = float(time[1])
        return minutes * 60 + seconds

    return f'{int(time // 60)}:{round(time % 60, 2) if time % 60 >= 10 else f"0{round(time % 60, 2)}"}'

def compare_greater(time1, time2):
    """Compares two times regardless of format.
    Args:
        time1 (float or str): Time in seconds or a string in the format "MM:SS" or "MM:SS.sss".
        time2 (float or str): Time in seconds or a string in the format "MM:SS" or "MM:SS.sss".
    """

    if isinstance(time1, str):
        time1 = format_time(time1)

    if isinstance(time2, str):
        time2 = format_time(time2)

    return time1 > time2

def event_to_dist(event_name):
    """Converts event names to their respective distances.

    Args:
        event_name (str): Name of the event.
    """

    nums = ""
    for char in event_name:
        if char.isnumeric() or char == '.':
            nums += char

    return float(nums)

def get_current_season():
    """Returns the current season.

    Returns:
        str: 'indoor' or 'outdoor'.
    """
    month = datetime.now().month

    return 'indoor' if month < 4 or month > 10 else 'outdoor'

def get_current_year():
    """Returns the current year.

    Returns:
        int: Current year.
    """
    now = datetime.now()
    month = now.month
    year = now.year

    return year if month < 11 else year + 1

