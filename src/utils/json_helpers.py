import datetime
import decimal

from bson import ObjectId
from bson.json_util import default


def object_hook(json_dict):

    if type(json_dict) is list:
        for idx, k in enumerate(json_dict):
            json_dict[idx] = object_hook(k)

    elif type(json_dict) is dict:
        for key, value in json_dict.items():
            json_dict[key] = object_hook(value)

    else:
        try:
            return parse_date(json_dict)
        except:
            pass

    return json_dict


def parse_date(text):

    formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S.%fZ',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%dT%H:%M:%SZ'
    ]

    for fmt in formats:
        try:
            return datetime.datetime.strptime(text, fmt)
        except ValueError:
            pass
    raise ValueError('no valid date format found')


def bson_to_json(o):
    if isinstance(o, ObjectId):
        return str(o)
    if isinstance(o, datetime.datetime):
        r = o.isoformat()
        return r + 'Z'
    elif isinstance(o, datetime.date):
        return o.isoformat()
    elif isinstance(o, datetime.time):
        r = o.isoformat()
        if o.microsecond:
            r = r[:12]
        return r
    elif isinstance(o, decimal.Decimal):
        return str(o)
    return default(o)
