import numpy as np
import pandas as pd

import utils
import json

OUTLIER_THRESHOLD = 0.04
TIMESERIES_THRESHOLD = 0.005
WINDOW_SIZE = 10
Z_SCORE_THRESHOLD = 0.0001

#OUTLIER_THRESHOLD = 999
data_path = 'data/Test_P09'

def get_point_key(data, point):
    for i in data:
        if data[i]["x"] == point["x"] and data[i]["y"] == point["y"] and data[i]["z"] == point["z"]:
            return i
    return None


def handle_mapping(user, device, item, user_data_index, user_data_item, target_data, result):
    mapping = utils.cal_curve_mapping(user_data_item, target_data)
    cleaned_mapping = []

    # Step 1: Remove spatial outliers
    for map_index, map_item in enumerate(mapping):
        if map_item["distance"] > OUTLIER_THRESHOLD:
            print(f"Spatial outlier removed at index {map_index}: {map_item}")
        else:
            cleaned_mapping.append(map_item)
    mapping = cleaned_mapping

    # Step 2: Remove duplicate mappings
    cleaned_mapping = []
    for map_index, map_item in enumerate(mapping):
        duplicate_found = next((j for j in cleaned_mapping if j["target"] == map_item["target"]), None)
        if duplicate_found:
            if map_item["distance"] < duplicate_found["distance"]:
                print(f"Duplicate mapping replaced at index {map_index}: {duplicate_found} -> {map_item}")
                cleaned_mapping.remove(duplicate_found)
                cleaned_mapping.append(map_item)
        else:
            cleaned_mapping.append(map_item)
    mapping = cleaned_mapping

    # Step 3: Detect and smooth timeseries outliers
    # Calculate euclidean distances between consecutive points
    distances = [0]
    for map_index in range(1, len(mapping)):
        map_item = mapping[map_index]
        prev_map_item = mapping[map_index - 1]
        euclidean_dist = utils.euclidean_distance(
            map_item["user"]["x"], map_item["user"]["y"], map_item["user"]["z"],
            prev_map_item["user"]["x"], prev_map_item["user"]["y"], prev_map_item["user"]["z"]
        )
        distances.append(euclidean_dist)

    # Convert distances to a pandas series
    distances = pd.Series(distances)

    # Detect outliers using z-score method
    distances_rolled = distances.rolling(window=WINDOW_SIZE)
    MA = distances_rolled.mean()
    MSTD = distances_rolled.std()
    z_scores = (distances - MA) / MSTD
    outliers = z_scores.abs() > Z_SCORE_THRESHOLD

    # Apply convolution to the window where outlier is detected
    if outliers.any():
        print(f"Applying convolution to smooth outliers...")
        window = distances[outliers]
        conv_kernel = np.ones(WINDOW_SIZE) / WINDOW_SIZE  # Simple averaging kernel
        smoothed_window = np.convolve(window, conv_kernel, mode='same')

        # Replace the window data with the smoothed data
        distances[outliers] = smoothed_window

    distances = [i["distance"] for i in mapping]
    avg_distance = np.mean(distances)
    median_distance = np.median(distances)

    result[user][device][item].append({
        "mapping": mapping,
        "avg_distance": avg_distance,
        "median_distance": median_distance
    })

    return user_data_item



# def handle_mapping(user, device, item, user_data_index, user_data_item, target_data, result):
#     mapping = utils.cal_curve_mapping(user_data_item, target_data)
#     cleaned_mapping = []
#
#     # Step 1: Remove spatial outliers
#     for map_index, map_item in enumerate(mapping):
#         if map_item["distance"] > OUTLIER_THRESHOLD:
#             print(f"Spatial outlier removed at index {map_index}: {map_item}")
#         else:
#             cleaned_mapping.append(map_item)
#     mapping = cleaned_mapping
#
#     # Step 2: Remove duplicate mappings
#     cleaned_mapping = []
#     for map_index, map_item in enumerate(mapping):
#         duplicate_found = next((j for j in cleaned_mapping if j["target"] == map_item["target"]), None)
#         if duplicate_found:
#             if map_item["distance"] < duplicate_found["distance"]:
#                 print(f"Duplicate mapping replaced at index {map_index}: {duplicate_found} -> {map_item}")
#                 cleaned_mapping.remove(duplicate_found)
#                 cleaned_mapping.append(map_item)
#         else:
#             cleaned_mapping.append(map_item)
#     mapping = cleaned_mapping
#
#     # Step 3: Remove timeseries outliers
#     # Calculate euclidean distances between consecutive points
#     distances = [0]
#     for map_index in range(1, len(mapping)):
#         map_item = mapping[map_index]
#         prev_map_item = mapping[map_index - 1]
#         euclidean_dist = utils.euclidean_distance(
#             map_item["user"]["x"], map_item["user"]["y"], map_item["user"]["z"],
#             prev_map_item["user"]["x"], prev_map_item["user"]["y"], prev_map_item["user"]["z"]
#         )
#         distances.append(euclidean_dist)
#
#     # Convert distances to a pandas series
#     distances = pd.Series(distances)
#
#     # Detect outliers using z-score method
#     distances_rolled = distances.rolling(window=WINDOW_SIZE)
#     MA = distances_rolled.mean()
#     MSTD = distances_rolled.std()
#     z_scores = (distances - MA) / MSTD
#     outliers = z_scores.abs() > Z_SCORE_THRESHOLD
#
#     # Remove outliers
#     cleaned_mapping = []
#     for map_index, map_item in enumerate(mapping):
#         if outliers[map_index]:
#             print(f"Timeseries outlier removed at index {map_index}: {map_item}")
#         else:
#             cleaned_mapping.append(map_item)
#     mapping = cleaned_mapping
#
#     distances = [i["distance"] for i in mapping]
#     avg_distance = np.mean(distances)
#     median_distance = np.median(distances)
#
#     result[user][device][item].append({
#         "mapping": mapping,
#         "avg_distance": avg_distance,
#         "median_distance": median_distance
#     })
#
#     return user_data_item



def main():
    with open(f"{data_path}/preprocessed_data.json", "r") as f:
        data = json.load(f)

    result = dict()
    for user, user_data in data.items():
        result[user] = dict()
        for device, device_data in user_data.items():
            result[user][device] = {
                "inner": [],
                "outer": []
            }
            for item in ["inner", "outer"]:
                for user_data_index, user_data_item in enumerate(device_data[item]["data"]):
                    cleaned_user_data_item = handle_mapping(user, device, item, user_data_index, user_data_item, device_data[item]["target"], result)
                    data[user][device][item]["data"][user_data_index] = cleaned_user_data_item  # update data with cleaned user_data_item

                with open(f"{data_path}/{user}_{device}_{item}.json", "w") as f:
                    json.dump(data[user][device][item]["data"], f)
                with open(f"{data_path}/{user}_{device}_{item}_target.json", "w") as f:
                    json.dump(device_data[item]["target"], f)

    with open(f"{data_path}/result.json", "w") as f:
        json.dump(result, f)
        print("Result saved")


    # with open("data/Test_P08/Target_Inner.json", "w") as f:
    #     json.dump(data["P02"]["Controller"]["inner"]["target"], f)
    #
    # with open("data/Test_P08/Target_Outer.json", "w") as f:
    #     json.dump(data["P02"]["Controller"]["outer"]["target"], f)
    #
    # with open("data/Test_P08/Data_Inner.json", "w") as f:
    #     json.dump(data["P02"]["Controller"]["inner"]["data"], f)
    #
    # with open("data/Test_P08/Data_Outer.json", "w") as f:
    #     json.dump(data["P02"]["Controller"]["outer"]["data"], f)


if __name__ == "__main__":
    main()
