from app.domain.enums import WorkspaceRole
from app.domain.permissions import has_workspace_role


def test_has_workspace_role_uses_owner_member_viewer_hierarchy() -> None:
    assert has_workspace_role(WorkspaceRole.OWNER, WorkspaceRole.MEMBER)
    assert has_workspace_role(WorkspaceRole.MEMBER, WorkspaceRole.VIEWER)
    assert not has_workspace_role(WorkspaceRole.VIEWER, WorkspaceRole.MEMBER)
