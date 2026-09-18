import json
from pathlib import Path
from calculations import analyze_match

data_file = (
    Path(__file__).parent.parent
    / "data"
    / "sample_points.json"
)
with data_file.open("r") as file:
    match_data = json.load(file)


results = analyze_match(match_data)

print("Match Summary")
print(f"Total Points: {results['total_points']}")
print(f"Wins: {results['wins']}")
print(f"Losses: {results['losses']}")
print(f"Average rally length: {results['average_rally_length']:.2f}")



