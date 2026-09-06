from uuid import uuid4

from sqlmodel import Session

from app.domain.enums import RelationSelectionMode
from app.models.relation import WorkspaceRelation
from app.models.transaction import Transaction
from app.models.workspace import WorkspaceMember
from app.services.relation_builder import RelationBuilder


def build_relation(workspace_id, *, selection_mode=RelationSelectionMode.DYNAMIC, rule_definition=None) -> WorkspaceRelation:
    return WorkspaceRelation(
        workspace_id=workspace_id,
        name="Trip Spend",
        description=None,
        selection_mode=selection_mode,
        rule_definition=rule_definition,
        created_by_user_id=uuid4(),
    )


def test_list_transactions_filters_by_workspace_members_and_rules(
    db_session: Session,
    workspace_member: WorkspaceMember,
    transaction_factory,
    other_user,
) -> None:
    keep = transaction_factory(note="trip dinner", amount=3200)
    transaction_factory(note="boring", amount=900)
    other_member = WorkspaceMember(
        workspace_id=workspace_member.workspace_id,
        user_id=other_user.id,
        role="member",
    )
    db_session.add(other_member)
    db_session.commit()
    outsider = Transaction(
        id=999,
        transaction_id=uuid4(),
        user_id=other_user.id,
        category_id=None,
        amount=4000,
        currency="USD",
        transaction_at=1725580800222,
        note="trip hotel",
        last_operation_key=f"1725580800222_{uuid4()}",
        version=1,
        deleted_at=None,
        created_at=1725580800222,
        updated_at=1725580800222,
    )
    db_session.add(outsider)
    db_session.commit()

    relation = build_relation(
        workspace_member.workspace_id,
        rule_definition={"note_contains": ["trip"], "amount_min": 1000},
    )

    items = RelationBuilder().list_transactions(db_session, relation)

    assert [item.id for item in items] == [keep.id, outsider.id]


def test_manual_relation_uses_manual_transaction_ids(
    db_session: Session,
    workspace_member: WorkspaceMember,
    transaction_factory,
) -> None:
    keep = transaction_factory(note="manual")
    transaction_factory(note="skip")
    relation = build_relation(
        workspace_member.workspace_id,
        selection_mode=RelationSelectionMode.MANUAL,
        rule_definition={"manual_transaction_ids": [keep.id]},
    )

    items = RelationBuilder().list_transactions(db_session, relation)

    assert [item.id for item in items] == [keep.id]


def test_hybrid_relation_unions_dynamic_and_manual(
    db_session: Session,
    workspace_member: WorkspaceMember,
    transaction_factory,
) -> None:
    dynamic_item = transaction_factory(note="trip")
    manual_item = transaction_factory(note="manual")
    relation = build_relation(
        workspace_member.workspace_id,
        selection_mode=RelationSelectionMode.HYBRID,
        rule_definition={"note_contains": ["trip"], "manual_transaction_ids": [manual_item.id]},
    )

    items = RelationBuilder().list_transactions(db_session, relation)

    assert {item.id for item in items} == {dynamic_item.id, manual_item.id}
