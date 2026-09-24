from langchain_core.tools import tool

from app.integrations.gmail import GmailIntegration


gmail = None


def get_gmail():
    global gmail

    if gmail is None:
        gmail = GmailIntegration()

    return gmail


@tool
def search_gmail_messages(
    query: str,
    max_results: int = 20,
):
    """
    Search Gmail messages using a Gmail search query.

    Examples:
    - newer_than:7d
    - is:unread
    - from:client@example.com
    - subject:project
    """

    messages = get_gmail().search_messages(
        query=query,
        max_results=max_results,
    )

    return [message.model_dump() for message in messages]


@tool
def get_gmail_message(message_id: str):
    """
    Get a specific Gmail message by its message ID.

    Use this when detailed information about an email
    is required.
    """

    message = get_gmail().get_message(message_id)

    if message is None:
        return {
            "message": "Gmail message not found."
        }

    return message.model_dump()