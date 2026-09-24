from app.integrations.gmail import GmailIntegration

print("Starting Gmail OAuth test...")

gmail = GmailIntegration()

print("Gmail authentication successful!")

messages = gmail.search_messages(
    query="newer_than:7d",
    max_results=5
)

print(f"Messages found: {len(messages)}")

for message in messages:
    print("\n---")
    print("ID:", message.id)
    print("Subject:", message.subject)
    print("Sender:", message.sender)