from datetime import date, datetime, timedelta
from decimal import Decimal

from flask.json.provider import DefaultJSONProvider


class AppJSONProvider(DefaultJSONProvider):
    ensure_ascii = False
    sort_keys = False

    @staticmethod
    def default(o):
        if isinstance(o, Decimal):
            return float(o)
        if isinstance(o, datetime):
            return o.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(o, date):
            return o.isoformat()
        if isinstance(o, timedelta):
            return str(o)
        return DefaultJSONProvider.default(o)
