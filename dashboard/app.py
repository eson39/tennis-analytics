import json
from pathlib import Path
from calculations import analyze_match, get_valid_shots, get_player_shots

data_file = (
    Path(__file__).parent.parent
    / "data"
    / "sample_points.json"
)
with data_file.open("r") as file:
    match_data = json.load(file)

results = analyze_match(match_data)
valid_shots = get_valid_shots(match_data)
p1_shots = get_player_shots(valid_shots, "player_1")
opponent_shots = get_player_shots(valid_shots, "opponent")

print("Match Summary")
print(f"Total Points: {results['total_points']}")
print(f"Wins: {results['wins']}")
print(f"Losses: {results['losses']}")
print(f"Average rally length: {results['average_rally_length']:.2f}")
print(f"Valid landings: {len(valid_shots)}")
print(f"Player 1 Shots: {len(p1_shots)}")
print(f"Opponent Shots: {len(opponent_shots)}")



