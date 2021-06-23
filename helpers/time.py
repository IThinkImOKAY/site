import time
import math

timestamp = int(time.time())

def age_string(time_utc):
    if timestamp - time_utc < 60:
        return "just now"
    elif timestamp - time_utc < 3600:
        return f"{math.floor((timestamp - time_utc)/60)} minutes ago"
    elif timestamp - time_utc < 3600*24:
        return f"{math.floor((timestamp - time_utc)/3600)} hours ago"
    elif timestamp - time_utc < 3600*24*30:
        return f"{math.floor((timestamp - time_utc)/(3600*24))} days ago"
    elif timestamp - time_utc < 3600*24*30*12:
        return f"{math.floor((timestamp - time_utc)/(3600*24*30))} months ago"
    else:
        return f"{math.floor((timestamp - time_utc)/(3600*24*30*12))} years ago"
