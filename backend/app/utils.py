import datetime as dt



def isoformat_to_timestamp(date: str):
    date = dt.datetime.fromisoformat(date[:-1])
    timestamp = dt.datetime.timestamp(date)
    return int(timestamp * 1000)

def timestamp_to_isoformat(timestamp: int):
    date = dt.datetime.fromtimestamp(float(timestamp/1000))
    isoformat = date.isoformat() + 'Z'
    _ = isoformat.replace(' ', 'T')
    return _

def timestamp_minus_day(timestamp: int):
    return timestamp - (86400 * 1000)