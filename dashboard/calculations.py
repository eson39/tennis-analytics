import json
import matplotlib.pyplot as plt
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


valid_shots = []
p1_shots = []
opponent_shots = []

for point in points:
    for shot in point["shots"]:
        if (
            shot["landing_x"] is not None
            and shot["landing_y"] is not None
        ):
            valid_shots.append(shot)

for shots in valid_shots: 
    if shots["hitter"] == "player_1": 
        p1_shots.append(shots)
    elif shots["hitter"] == "opponent":
        opponent_shots.append(shots)

deep_right_count = 0

for shot in p1_shots:
    if shot["landing_x"] >= 2/3 and shot["landing_y"] >= 2/3:
        deep_right_count += 1

if len(p1_shots) > 0:
    deep_right_percentage = (deep_right_count / len(p1_shots)) * 100
else:
    deep_right_percentage = 0

p1_weights = []

for shot in p1_shots:
    p1_weights.append(100 / len(p1_shots))

opponent_weights = []

for shot in opponent_shots:
    opponent_weights.append(100 / len(opponent_shots))

p1_x = []
p1_y = []

for shot in p1_shots: 
    p1_x.append(shot["landing_x"])
    p1_y.append(shot["landing_y"])

opponent_x = []
opponent_y = []

for shot in opponent_shots:
    opponent_x.append(shot["landing_x"])
    opponent_y.append(shot["landing_y"])

assert len(p1_x) == len(p1_y)
assert len(opponent_x) == len(opponent_y)


print("Valid landing shots:", len(valid_shots))
print("Player 1 valid shots:", len(p1_shots))
print("Opponent valid shots:", len(opponent_shots))
print("Player 1 x values:", len(p1_x))
print("Player 1 y values:", len(p1_y))
print("Opponent x values:", len(opponent_x))
print("Opponent y values:", len(opponent_y))
print("Total points:", total_points)
print("Wins:", wins)
print("Losses:", losses)
print("Average rally length:", average_rally_length)
print(deep_right_count)
print("Player 1 deep-right percentage:", deep_right_percentage)
print("Player 1 total weight:", sum(p1_weights))
print("Opponent total weight:", sum(opponent_weights))


plt.figure()
p1_percentages, p1_x_edges, p1_y_edges, p1_image = plt.hist2d(
    p1_x, p1_y, 
    bins=3, 
    range=[[0, 1], [0, 1]],
    vmin=0,
    vmax=100,
    weights=p1_weights
)
print("Player 1 percentages:", p1_percentages)
plt.title("Player 1 Shot Landings")
plt.xlabel("Court width (0 = receiver's left, 1 = right)")
plt.ylabel("Court depth (0 = net, 1 = baseline)")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.colorbar(label="Percentage of valid landings")
for x_index in range(3):
    for y_index in range(3):
        plt.text(
            (p1_x_edges[x_index] + p1_x_edges[x_index + 1]) / 2,
            (p1_y_edges[y_index] + p1_y_edges[y_index + 1]) / 2,
            f"{p1_percentages[x_index, y_index]:.1f}%",
            ha="center",
            va="center",
            color="white"
        )

plt.figure()
opponent_percentages, opponent_x_edges, opponent_y_edges, opponent_image = plt.hist2d(
    opponent_x, opponent_y, 
    bins=3, 
    range=[[0, 1], [0, 1]],
    vmin=0,
    vmax=100,
    weights=opponent_weights
)
print("Opponent percentages:", opponent_percentages)
plt.title("Opponent Shot Landings")
plt.xlabel("Court width (0 = receiver's left, 1 = right)")
plt.ylabel("Court depth (0 = net, 1 = baseline)")
plt.xlim(0, 1)
plt.ylim(0, 1)
plt.colorbar(label="Percentage of valid landings")
for x_index in range(3):
    for y_index in range(3):
        plt.text(
            (opponent_x_edges[x_index] + opponent_x_edges[x_index + 1]) / 2,
            (opponent_y_edges[y_index] + opponent_y_edges[y_index + 1]) / 2,
            f"{opponent_percentages[x_index, y_index]:.1f}%",
            ha="center",
            va="center",
            color="white"
        )


plt.show()
