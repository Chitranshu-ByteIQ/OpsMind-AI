from app.schemas.actions import (
    ActionRequest,
    ActionStatus,
    ActionResult,
)

from app.guardrails.policies import requires_approval


def validate_action(action: ActionRequest) -> ActionRequest:
    """
    Validate an action and determine whether approval is required.
    """

    action.requires_approval = requires_approval(
        action.action_type
    )

    return action


def approve_action(action: ActionRequest) -> ActionResult:
    """
    Mark an action as approved.

    This function does not execute the action.
    It only records that the action has been approved.
    """

    return ActionResult(
        action_type=action.action_type,
        tool_name=action.tool_name,
        status=ActionStatus.APPROVED,
        message="Action approved by human.",
        data=action.parameters,
    )


def reject_action(action: ActionRequest) -> ActionResult:
    """
    Mark an action as rejected.
    """

    return ActionResult(
        action_type=action.action_type,
        tool_name=action.tool_name,
        status=ActionStatus.REJECTED,
        message="Action rejected by human.",
        data=action.parameters,
    )