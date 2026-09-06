from collections import defaultdict
from typing import Iterable

from sqlmodel import Session

from app.domain.constants import SUPPORTED_GROUP_BY_VALUES
from app.models.transaction import Transaction
from app.schemas.analytics import AnalyticsQuery, AnalyticsResultRow
from app.services.relations import RelationService


class AnalyticsQueryError(ValueError):
    pass


class AnalyticsService:
    def validate_query(self, query: AnalyticsQuery) -> AnalyticsQuery:
        if query.group_by and query.group_by not in SUPPORTED_GROUP_BY_VALUES:
            raise AnalyticsQueryError(f"unsupported group_by: {query.group_by}")

        if query.group_by not in {None, "currency"} and query.currency is None:
            raise AnalyticsQueryError("mixed-currency aggregation requires a currency filter or currency grouping")

        return query

    def spending(
        self,
        session: Session,
        relation_service: RelationService,
        workspace_id,
        relation_id,
        user_id,
        query: AnalyticsQuery,
    ) -> list[AnalyticsResultRow]:
        validated = self.validate_query(query)
        items = self._filter_transactions(
            relation_service.list_transactions(session, workspace_id, relation_id, user_id),
            validated,
        )
        return self._aggregate(items, validated.group_by)

    def trends(
        self,
        session: Session,
        relation_service: RelationService,
        workspace_id,
        relation_id,
        user_id,
        query: AnalyticsQuery,
    ) -> list[AnalyticsResultRow]:
        validated = self.validate_query(AnalyticsQuery(**{**query.model_dump(), "group_by": validated_group(query.group_by, "month")}))
        items = self._filter_transactions(
            relation_service.list_transactions(session, workspace_id, relation_id, user_id),
            validated,
        )
        return self._aggregate(items, validated.group_by)

    def breakdown(
        self,
        session: Session,
        relation_service: RelationService,
        workspace_id,
        relation_id,
        user_id,
        query: AnalyticsQuery,
    ) -> list[AnalyticsResultRow]:
        default_group_by = validated_group(query.group_by, "category")
        validated = self.validate_query(AnalyticsQuery(**{**query.model_dump(), "group_by": default_group_by}))
        items = self._filter_transactions(
            relation_service.list_transactions(session, workspace_id, relation_id, user_id),
            validated,
        )
        return self._aggregate(items, validated.group_by)

    def _filter_transactions(self, items: list[Transaction], query: AnalyticsQuery) -> list[Transaction]:
        filtered = items
        if query.currency is not None:
            filtered = [item for item in filtered if item.currency == query.currency]
        if query.from_ts is not None:
            filtered = [item for item in filtered if item.transaction_at >= query.from_ts]
        if query.to_ts is not None:
            filtered = [item for item in filtered if item.transaction_at <= query.to_ts]
        return filtered

    def _aggregate(self, items: Iterable[Transaction], group_by: str | None) -> list[AnalyticsResultRow]:
        buckets: dict[tuple[str, str], int] = defaultdict(int)
        for item in items:
            key = self._key_for(item, group_by)
            buckets[(key, item.currency)] += item.amount
        return [
            AnalyticsResultRow(key=key, amount=amount, currency=currency)
            for (key, currency), amount in sorted(buckets.items())
        ]

    def _key_for(self, item: Transaction, group_by: str | None) -> str:
        if group_by is None:
            return "total"
        if group_by == "currency":
            return item.currency
        if group_by == "category":
            return str(item.category_id)
        if group_by == "user":
            return str(item.user_id)
        if group_by == "month":
            return str(item.transaction_at)[:6]
        if group_by == "user,category":
            return f"{item.user_id},{item.category_id}"
        if group_by == "month,currency":
            return f"{str(item.transaction_at)[:6]},{item.currency}"
        if group_by == "month,user":
            return f"{str(item.transaction_at)[:6]},{item.user_id}"
        raise AnalyticsQueryError(f"unsupported group_by: {group_by}")


def validated_group(group_by: str | None, default: str) -> str:
    return group_by or default
