from app.domain.constants import SUPPORTED_GROUP_BY_VALUES
from app.schemas.analytics import AnalyticsQuery


class AnalyticsQueryError(ValueError):
    pass


class AnalyticsService:
    def validate_query(self, query: AnalyticsQuery) -> AnalyticsQuery:
        if query.group_by and query.group_by not in SUPPORTED_GROUP_BY_VALUES:
            raise AnalyticsQueryError(f"unsupported group_by: {query.group_by}")

        if query.group_by not in {None, "currency"} and query.currency is None:
            raise AnalyticsQueryError("mixed-currency aggregation requires a currency filter or currency grouping")

        return query
