from app.domain.enums import WorkspaceRole


WORKSPACE_ROLE_ORDER = {
    WorkspaceRole.VIEWER: 1,
    WorkspaceRole.MEMBER: 2,
    WorkspaceRole.OWNER: 3,
}


def has_workspace_role(current_role: WorkspaceRole, required_role: WorkspaceRole) -> bool:
    return WORKSPACE_ROLE_ORDER[current_role] >= WORKSPACE_ROLE_ORDER[required_role]
