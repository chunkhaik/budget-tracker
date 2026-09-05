from enum import StrEnum


class WorkspaceRole(StrEnum):
    OWNER = "owner"
    MEMBER = "member"
    VIEWER = "viewer"


class CategoryType(StrEnum):
    EXPENSE = "expense"
    INCOME = "income"
    TRANSFER = "transfer"


class RelationSelectionMode(StrEnum):
    MANUAL = "manual"
    DYNAMIC = "dynamic"
    HYBRID = "hybrid"


class TransactionCommandType(StrEnum):
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
