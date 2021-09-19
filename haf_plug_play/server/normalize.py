import decimal
from datetime import datetime
from haf_plug_play.utils.tools import UTC_TIMESTAMP_FORMAT

def populate_by_schema(data, fields):
    result = {}
    for i in range(len(fields)):
        result[fields[i]] = data[i]
    return result

def normalize_types(data):
    if isinstance(data, dict):
        for k in data:
            if isinstance(data[k], decimal.Decimal):
                data[k] = float(data[k])
            elif isinstance(data[k], datetime):
                data[k] = datetime.strftime(data[k], UTC_TIMESTAMP_FORMAT)
    return data
