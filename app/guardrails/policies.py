from app.schemas.actions import ActionType


# Actions that can change external systems
WRITE_ACTIONS = {
    ActionType.CREATE,
    ActionType.UPDATE,
    ActionType.DELETE,
    ActionType.SEND,
}


def requires_approval(action_type: ActionType) -> bool:
    """
    Determine whether an action requires human approval.
    """

    return action_type in WRITE_ACTIONS