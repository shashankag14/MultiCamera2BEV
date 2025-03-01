import json
import numpy as np
import os


def load_points(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as file:
            print(f"Loading points from {file_path}")
            points_data = json.load(file)
            np_points_data = [np.array(pt, dtype=np.float32) for pt in points_data]
            print(f"Loaded points: {np_points_data}")
            return np_points_data
    else:
        ValueError("No saved points found.")
        exit(1)


def save_points(file_path, points_data):
    points_data_as_lists = [pt.tolist() for pt in points_data]
    assert points_data_as_lists, "No points to save"
    with open(file_path, 'w') as file:
        json.dump(points_data_as_lists, file)
    print(f"Saved points to {file_path}")
