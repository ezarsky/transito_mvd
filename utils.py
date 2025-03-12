import pandas as pd

def round_time_5min(timestamp):
    unix_zero = pd.Timestamp(0)
    unix_five_mins = round((timestamp - unix_zero)/pd.Timedelta(minutes=5))
    return pd.to_datetime(unix_five_mins * 5 * 60e9)