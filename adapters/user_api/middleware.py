import datetime
import json

from application.user_application.dataclases import BaseModel


def _get_duration_components(duration):
    days = duration.days
    seconds = duration.seconds
    microseconds = duration.microseconds

    minutes = seconds // 60
    seconds = seconds % 60

    hours = minutes // 60
    minutes = minutes % 60

    return days, hours, minutes, seconds, microseconds


def duration_iso_string(duration):
    if duration < datetime.timedelta(0):
        sign = '-'
        duration *= -1
    else:
        sign = ''

    days, hours, minutes, seconds, microseconds = _get_duration_components(duration)
    ms = '.{:06d}'.format(microseconds) if microseconds else ""
    return '{}P{}DT{:02d}H{:02d}M{:02d}{}S'.format(sign, days, hours, minutes, seconds, ms)


class BaseJSONEncoder(json.JSONEncoder):
    """
    JSONEncoder subclass that knows how to encode date/time
    """
    def default(self, o):
        # See "Date Time String Format" in the ECMA-262 specification.
        if isinstance(o, datetime.datetime):
            r = o.isoformat()
            if o.microsecond:
                r = r[:23] + r[26:]
            if r.endswith('+00:00'):
                r = r[:-6] + 'Z'
            return r
        elif isinstance(o, datetime.date):
            return o.isoformat()
        elif isinstance(o, datetime.time):
            r = o.isoformat()
            if o.microsecond:
                r = r[:12]
            return r
        elif isinstance(o, datetime.timedelta):
            return duration_iso_string(o)
        else:
            return super().default(o)


class ChatSerializer(BaseJSONEncoder):
    def default(self, o):
        if isinstance(o, BaseModel):
            forbidden_keys = ['_sa_instance_state', 'user']
            result = {}
            for key, value in o.__dict__.items():
                if key not in forbidden_keys:
                    result[key] = value
            return result
        return super().default(o)


class JSONTranslator:

    def process_response(self, req, resp, resource, req_succeeded):
        resp.set_header('Content-Type', 'application/json')
        resp.body = json.dumps(resp.body, cls=ChatSerializer)
