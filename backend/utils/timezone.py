import zoneinfo
from datetime import datetime
from datetime import timezone as datetime_timezone

from backend.core.config import settings


class TimeZone:
    def __init__(self) -> None:
        self.tz_info = zoneinfo.ZoneInfo(settings.timezone.datetime_timezone)

    def now(self) -> datetime:
        return datetime.now(self.tz_info)

    def from_datetime(self, t: datetime) -> datetime:
        return t.astimezone(self.tz_info)

    def from_str(
        self,
        t_str: str,
        format_str: str = settings.timezone.datetime_format,
    ) -> datetime:
        return datetime.strptime(t_str, format_str).replace(tzinfo=self.tz_info)

    @staticmethod
    def to_str(
        t: datetime,
        format_str: str = settings.timezone.datetime_format,
    ) -> str:
        return t.strftime(format_str)

    @staticmethod
    def to_utc(t: datetime | int) -> datetime:
        if isinstance(t, datetime):
            return t.astimezone(datetime_timezone.utc)
        return datetime.fromtimestamp(t, tz=datetime_timezone.utc)


timezone: TimeZone = TimeZone()
