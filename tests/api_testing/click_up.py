from app.integrations.clickup import ClickUpIntegration

print("Starting ClickUp API test...\n")

clickup = ClickUpIntegration()

print("========== RAW TEAMS RESPONSE ==========")

teams = clickup.get_teams()

print("Type:", type(teams))
print("Value:")
print(teams)

print("\n========== TEAM STRUCTURE ==========")

if isinstance(teams, list):
    print("Number of teams:", len(teams))

    for index, team in enumerate(teams):
        print(f"\nTeam #{index + 1}")
        print("Type:", type(team))
        print("Value:", team)

elif isinstance(teams, dict):
    print("Dictionary keys:", teams.keys())