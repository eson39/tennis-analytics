import json
from pathlib import Path

data_file = (
    Path(__file__).parent.parent
    / "data"
    / "sample_points.json"
)

with data_file.open("r") as file: 
    match_data = json.load(file)

points = match_data["points"]

total_points = len(points)

wins = 0
losses = 0

for point in points:
    if point["outcome"] == "won":
        wins += 1
    elif point["outcome"] == "lost":
        losses += 1

total_shots = 0

for point in points:
    total_shots += point["rally_length"]

if total_points > 0:
    average_rally_length = total_shots / total_points
else:
    average_rally_length = 0



print("Total points:", total_points)
print("Wins:", wins)
print("Losses:", losses)
print("Average rally length:", average_rally_length)

