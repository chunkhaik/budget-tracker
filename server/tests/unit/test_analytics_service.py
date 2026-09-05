import pytest

from app.schemas.analytics import AnalyticsQuery
from app.services.analytics import AnalyticsQueryError, AnalyticsService


def test_validate_query_accepts_supported_group_by_without_currency_when_grouped_by_currency() -> None:
    query = AnalyticsQuery(group_by="currency")

    assert AnalyticsService().validate_query(query) is query


def test_validate_query_rejects_unsupported_group_by() -> None:
    with pytest.raises(AnalyticsQueryError, match="unsupported group_by"):
        AnalyticsService().validate_query(AnalyticsQuery(group_by="weekday"))


def test_validate_query_requires_currency_for_mixed_currency_aggregation() -> None:
    with pytest.raises(AnalyticsQueryError, match="mixed-currency aggregation"):
        AnalyticsService().validate_query(AnalyticsQuery(group_by="category"))
