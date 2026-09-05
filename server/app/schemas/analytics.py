from app.schemas.common import APIModel


class AnalyticsQuery(APIModel):
    group_by: str | None = None
    currency: str | None = None
    from_ts: int | None = None
    to_ts: int | None = None


class AnalyticsResultRow(APIModel):
    key: str
    amount: int
    currency: str
