from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from app.schemas.gmail import GmailMessage


class GmailIntegration:
    """Client for interacting with Gmail API."""

    SCOPES = [
        "https://www.googleapis.com/auth/gmail.readonly"
    ]

    def __init__(
        self,
        credentials_path: str = "credentials/credentials.json",
        token_path: str = "credentials/token.json",
    ):
        self.credentials_path = Path(
            credentials_path
        )

        self.token_path = Path(token_path)

        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail using OAuth2."""

        credentials = None

        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                self.token_path,
                self.SCOPES,
            )

        if not credentials or not credentials.valid:

            if (
                credentials
                and credentials.expired
                and credentials.refresh_token
            ):
                credentials.refresh(
                    Request()
                )

            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.SCOPES,
                )

                credentials = flow.run_local_server(
                    port=0
                )

            self.token_path.parent.mkdir(
                parents=True,
                exist_ok=True,
            )

            self.token_path.write_text(
                credentials.to_json()
            )

        return build(
            "gmail",
            "v1",
            credentials=credentials,
        )

    def search_messages(
        self,
        query: str,
        max_results: int = 20,
    ) -> list[GmailMessage]:
        """Search Gmail messages."""

        response = (
            self.service.users()
            .messages()
            .list(
                userId="me",
                q=query,
                maxResults=max_results,
            )
            .execute()
        )

        messages = []

        for message in response.get(
            "messages",
            [],
        ):
            gmail_message = self.get_message(
                message["id"]
            )

            if gmail_message:
                messages.append(
                    gmail_message
                )

        return messages

    def get_message(
        self,
        message_id: str,
    ) -> GmailMessage | None:
        """Get a Gmail message by ID."""

        message = (
            self.service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
            .execute()
        )

        payload = message.get(
            "payload",
            {},
        )

        headers = payload.get(
            "headers",
            []
        )

        header_map = {
            header["name"].lower(): header["value"]
            for header in headers
        }

        body = self._extract_body(
            payload
        )

        return GmailMessage(
            id=message["id"],
            thread_id=message["threadId"],
            sender=header_map.get(
                "from",
                "",
            ),
            recipients=self._split_recipients(
                header_map.get(
                    "to",
                    "",
                )
            ),
            subject=header_map.get(
                "subject",
                "",
            ),
            body=body,
            snippet=message.get(
                "snippet"
            ),
            received_at=self._timestamp_to_datetime(
                message.get(
                    "internalDate"
                )
            ),
            labels=message.get(
                "labelIds",
                [],
            ),
            is_read=(
                "UNREAD"
                not in message.get(
                    "labelIds",
                    [],
                )
            ),
        )

    @staticmethod
    def _split_recipients(
        recipients: str,
    ) -> list[str]:
        """Convert recipient string into a list."""

        if not recipients:
            return []

        return [
            recipient.strip()
            for recipient in recipients.split(",")
            if recipient.strip()
        ]

    def _extract_body(
        self,
        payload: dict,
    ) -> str:
        """Extract plain-text body from Gmail payload."""

        import base64

        if payload.get("body", {}).get("data"):
            return base64.urlsafe_b64decode(
                payload["body"]["data"]
            ).decode(
                "utf-8",
                errors="ignore",
            )

        for part in payload.get(
            "parts",
            [],
        ):
            if part.get("mimeType") == "text/plain":
                data = part.get(
                    "body",
                    {},
                ).get("data")

                if data:
                    return base64.urlsafe_b64decode(
                        data
                    ).decode(
                        "utf-8",
                        errors="ignore",
                    )

            if part.get("parts"):
                body = self._extract_body(
                    part
                )

                if body:
                    return body

        return ""

    @staticmethod
    def _timestamp_to_datetime(
        timestamp: str | None,
    ):
        """Convert Gmail timestamp to datetime."""

        if not timestamp:
            return None

        from datetime import datetime, timezone

        return datetime.fromtimestamp(
            int(timestamp) / 1000,
            tz=timezone.utc,
        )